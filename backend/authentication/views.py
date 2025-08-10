from rest_framework import viewsets, status, permissions
from rest_framework.response import Response
from rest_framework.decorators import action
from django.contrib.auth.models import User
from django.core.exceptions import PermissionDenied
from .models import UserProfile, NotificationPreferences
from doctors.models import Doctor
from patients.models import Patient
from .serializers import UserSerializer, NotificationPreferencesSerializer, AdminUserUpdateSerializer
from django.contrib.auth import authenticate
from rest_framework.authtoken.models import Token
from django_otp.plugins.otp_totp.models import TOTPDevice
import pyotp
import qrcode
import io
import base64
from django.db import transaction
from django.contrib.auth.hashers import make_password
from django.conf import settings
import secrets
import logging
from rest_framework.pagination import PageNumberPagination
from .permissions import IsAdminRole


class UserPagination(PageNumberPagination):
    page_size = 10
    page_size_query_param = 'page_size'

class UserViewSet(viewsets.ModelViewSet):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    @action(detail=False, methods=['post'], permission_classes=[permissions.AllowAny])
    def register(self, request):
        serializer = UserSerializer(data=request.data)
        if serializer.is_valid():
            user = serializer.save()
            
            # Determina tipul de utilizator din request
            user_type = request.data.get('user_type', 'patient')
            
            # Creeaza UserProfile cu rolul corespunzator
            UserProfile.objects.create(user=user, role=user_type)
            
            # Creeaza Doctor sau Patient
            if user_type == 'doctor':
                Doctor.objects.create(
                    user=user,
                    speciality=request.data.get('speciality', 'General')
                )
            elif user_type == 'patient':
                Patient.objects.create(user=user)
            
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    @action(detail=False, methods=['post'], permission_classes=[permissions.AllowAny])
    def login(self, request):
        username = request.data.get('username')
        password = request.data.get('password')

        from django.core.cache import cache
        import logging

        ip = request.META.get('REMOTE_ADDR')
        failed_attempts_key = f"login_failed_{username}_{ip}"
        lockout_key = f"login_lockout_{username}_{ip}"
        logger = logging.getLogger(__name__)

        if cache.get(lockout_key):
            return Response(
                {'error': 'Too many failed attempts. Please try again in 15 minutes.'},
                status=status.HTTP_429_TOO_MANY_REQUESTS,
            )

        user = authenticate(username=username, password=password)

        if user is not None:
            if not user.is_active:
                return Response({'error': 'Account is inactive'}, status=status.HTTP_403_FORBIDDEN)

            # reset failed attempts on successful login
            cache.delete(failed_attempts_key)
            cache.delete(lockout_key)

            profile = UserProfile.objects.get(user=user)

            if profile.two_fa_enabled:
                return Response({
                    'message': '2FA required',
                    'user_id': user.id,
                    'requires_2fa': True
                }, status=status.HTTP_200_OK)

            Token.objects.filter(user=user).delete()
            token = Token.objects.create(user=user)

            # Get additional IDs based on role
            doctor_id = None
            patient_id = None

            if profile.role == 'doctor' and hasattr(user, 'doctor'):
                doctor_id = user.doctor.id
            elif profile.role == 'patient' and hasattr(user, 'patient'):
                patient_id = user.patient.id

            response = Response({
                'user_id': user.id,
                'email': user.email,
                'requires_2fa': False,
                'role': profile.role,
                'first_name': user.first_name,
                'last_name': user.last_name,
                'doctor_id': doctor_id,
                'patient_id': patient_id,
                'two_fa_enabled': profile.two_fa_enabled,
                'token': token.key,
            }, status=status.HTTP_200_OK)
            secure = not getattr(settings, 'DEBUG', False)
            response.set_cookie(
                'refresh_token',
                token.key,
                httponly=True,
                secure=secure,
                samesite='Strict'
            )
            # Log successful login
            logger.info(
                f"Successful login for user {user.username} from IP {ip}"
            )
            return response
        else:
            failed_attempts = cache.get(failed_attempts_key, 0) + 1
            cache.set(failed_attempts_key, failed_attempts, timeout=900)  # 15 minute
            logger.warning(
                f"Failed login attempt #{failed_attempts} for username {username} from IP {ip}"
            )

            if failed_attempts >= 5:
                cache.set(lockout_key, True, timeout=900)
                logger.error(
                    f"User {username} locked out due to too many failed login attempts from IP {ip}"
                )
                return Response(
                    {
                        'error': 'Too many failed login attempts. Account locked for 15 minutes.'
                    },
                    status=status.HTTP_429_TOO_MANY_REQUESTS,
                )

            return Response(
                {
                    'error': f'Invalid credentials. {5 - failed_attempts} attempts remaining.'
                },
                status=status.HTTP_401_UNAUTHORIZED,
            )

    @action(detail=False, methods=["post"], permission_classes=[permissions.AllowAny])
    def refresh(self, request):
        token_key = request.COOKIES.get("refresh_token")
        if not token_key:
            return Response(
                {"error": "No refresh token provided"},
                status=status.HTTP_401_UNAUTHORIZED,
            )
        try:
            token = Token.objects.get(key=token_key)
        except Token.DoesNotExist:
            return Response(
                {"error": "Invalid refresh token"},
                status=status.HTTP_401_UNAUTHORIZED,
            )

        user = token.user
        token.delete()
        new_token = Token.objects.create(user=user)
        response = Response({"token": new_token.key}, status=status.HTTP_200_OK)
        secure = not getattr(settings, "DEBUG", False)
        response.set_cookie(
            "refresh_token",
            new_token.key,
            httponly=True,
            secure=secure,
            samesite="Strict",
        )
        return response

    @action(detail=False, methods=['post'], permission_classes=[permissions.IsAuthenticated])
    def logout(self, request):
        Token.objects.filter(user=request.user).delete()
        response = Response({'message': 'Logged out'}, status=status.HTTP_200_OK)
        response.delete_cookie('refresh_token')
        return response
    
    @action(detail=False, methods=['post'], permission_classes=[permissions.IsAuthenticated])
    def enable_2fa(self, request):
        user = request.user
        profile = UserProfile.objects.get(user=user)
        
        if profile.two_fa_enabled:
            return Response({'error': '2FA is already enabled'}, status=status.HTTP_400_BAD_REQUEST)
        
        # Sterge dispozitivele TOTP existente
        TOTPDevice.objects.filter(user=user).delete()
        
        # Genereaza o cheie secreta pentru TOTP
        key = pyotp.random_base32()
        
        # Creeaza dispozitivul TOTP (dar nu il confirma inca)
        device = TOTPDevice.objects.create(
            user=user,
            name=f"{user.username}'s device",
            key=key,
            confirmed=False
        )
        
        # Genereaza un URL pentru configurarea aplicatiei de autentificare
        totp_url = pyotp.totp.TOTP(key).provisioning_uri(
            name=user.email,
            issuer_name="Medical Appointments System"
        )
        
        # Genereaza QR code
        qr = qrcode.QRCode(version=1, box_size=10, border=5)
        qr.add_data(totp_url)
        qr.make(fit=True)
        
        img = qr.make_image(fill_color="black", back_color="white")
        buffer = io.BytesIO()
        img.save(buffer, format='PNG')
        buffer.seek(0)
        
        qr_code_base64 = base64.b64encode(buffer.getvalue()).decode()
        qr_code_url = f"data:image/png;base64,{qr_code_base64}"
        
        return Response({
            'message': '2FA setup initiated',
            'key': key,
            'totp_url': totp_url,
            'qr_code': qr_code_url
        }, status=status.HTTP_200_OK)
    
    @action(detail=False, methods=['post'], permission_classes=[permissions.IsAuthenticated])
    def confirm_2fa(self, request):
        user = request.user
        code = request.data.get('code')
        
        if not code:
            return Response({'error': 'Verification code is required'}, status=status.HTTP_400_BAD_REQUEST)
        
        # Rate limiting pentru setup
        from django.core.cache import cache
        setup_attempts_key = f"2fa_setup_attempts_{user.id}"
        
        setup_attempts = cache.get(setup_attempts_key, 0)
        if setup_attempts >= 10:  # Maxim 10 incercari pentru setup
            return Response({
                'error': 'Too many setup attempts. Please try again in 10 minutes.'
            }, status=status.HTTP_429_TOO_MANY_REQUESTS)
        
        try:
            # Gaseste dispozitivul TOTP neconfirmat
            device = TOTPDevice.objects.get(user=user, confirmed=False)
            
            totp = pyotp.TOTP(device.key)
            if totp.verify(code, valid_window=1):  # Setup poate avea toleranta mai mare
                # Confirma dispozitivul si activeaza 2FA
                device.confirmed = True
                device.save()
                
                profile = UserProfile.objects.get(user=user)
                profile.two_fa_enabled = True
                profile.save()
                
                # RESET failed attempts
                cache.delete(setup_attempts_key)
                
                # LOG: Successful 2FA setup
                import logging
                logger = logging.getLogger(__name__)
                logger.info(f"User {user.username} successfully enabled 2FA from IP {request.META.get('REMOTE_ADDR')}")
                
                return Response({
                    'message': '2FA has been enabled successfully'
                }, status=status.HTTP_200_OK)
            else:
                # INCREMENT setup attempts
                cache.set(setup_attempts_key, setup_attempts + 1, timeout=600)  # 10 minute
                
                return Response({'error': 'Invalid verification code'}, status=status.HTTP_400_BAD_REQUEST)
                
        except TOTPDevice.DoesNotExist:
            return Response({'error': 'No pending 2FA setup found'}, status=status.HTTP_404_NOT_FOUND)
    
    @action(detail=False, methods=['post'], permission_classes=[permissions.IsAuthenticated])
    def disable_2fa(self, request):
        user = request.user
        profile = UserProfile.objects.get(user=user)
        
        if not profile.two_fa_enabled:
            return Response({'error': '2FA is not enabled'}, status=status.HTTP_400_BAD_REQUEST)
        
        # Sterge toate dispozitivele TOTP
        TOTPDevice.objects.filter(user=user).delete()
        
        # Dezactiveaza 2FA in profil
        profile.two_fa_enabled = False
        profile.save()
        
        return Response({
            'message': '2FA has been disabled'
        }, status=status.HTTP_200_OK)

    @action(detail=False, methods=['post'], permission_classes=[permissions.IsAuthenticated])
    def regenerate_backup_codes(self, request):
        user = request.user
        profile = UserProfile.objects.get(user=user)

        # Generate 10 random backup codes
        codes = [secrets.token_hex(4) for _ in range(10)]
        hashed_codes = [make_password(code) for code in codes]

        profile.backup_codes = hashed_codes
        profile.save()

        return Response({'backup_codes': codes}, status=status.HTTP_200_OK)
    
    @action(detail=False, methods=['post'], permission_classes=[permissions.AllowAny])
    def verify_2fa(self, request):
        user_id = request.data.get('user_id')
        code = request.data.get('code')
        
        if not user_id or not code:
            return Response({'error': 'User ID and code are required'}, status=status.HTTP_400_BAD_REQUEST)
        
        # Rate limiting check
        from django.core.cache import cache
        import time
        
        # Key pentru tracking failed attempts
        failed_attempts_key = f"2fa_failed_attempts_{user_id}"
        lockout_key = f"2fa_lockout_{user_id}"
        
        # Verifica daca utilizatorul e locked out
        if cache.get(lockout_key):
            return Response({
                'error': 'Too many failed attempts. Please try again in 15 minutes.'
            }, status=status.HTTP_429_TOO_MANY_REQUESTS)
        
        try:
            user = User.objects.get(id=user_id)
            device = TOTPDevice.objects.get(user=user, confirmed=True)
            
            # Window mai strict si logging
            totp = pyotp.TOTP(device.key)
            
            # Verifica codul cu window redus (mai sigur)
            if totp.verify(code, valid_window=0):  # Doar codul exact, fara toleranta
                # SUCCES: Reseteaza failed attempts
                cache.delete(failed_attempts_key)
                cache.delete(lockout_key)
                
                # LOG: Successful 2FA
                import logging
                logger = logging.getLogger(__name__)
                logger.info(f"Successful 2FA login for user {user.username} from IP {request.META.get('REMOTE_ADDR')}")
                
                Token.objects.filter(user=user).delete()
                token = Token.objects.create(user=user)
                profile = UserProfile.objects.get(user=user)
                
                doctor_id = None
                patient_id = None
                
                if profile.role == 'doctor' and hasattr(user, 'doctor'):
                    doctor_id = user.doctor.id
                elif profile.role == 'patient' and hasattr(user, 'patient'):
                    patient_id = user.patient.id
                
                response = Response({
                    'user_id': user.id,
                    'email': user.email,
                    'role': profile.role,
                    'first_name': user.first_name,
                    'last_name': user.last_name,
                    'doctor_id': doctor_id,
                    'patient_id': patient_id,
                    'two_fa_enabled': profile.two_fa_enabled,
                    'token': token.key,
                }, status=status.HTTP_200_OK)
                secure = not getattr(settings, 'DEBUG', False)
                response.set_cookie(
                    'refresh_token',
                    token.key,
                    httponly=True,
                    secure=secure,
                    samesite='Strict'
                )
                return response
            else:
                # FAILED: Incrementeaza failed attempts
                failed_attempts = cache.get(failed_attempts_key, 0) + 1
                cache.set(failed_attempts_key, failed_attempts, timeout=900)  # 15 minute
                
                # LOG: Failed 2FA attempt
                import logging
                logger = logging.getLogger(__name__)
                logger.warning(f"Failed 2FA attempt #{failed_attempts} for user {user.username} from IP {request.META.get('REMOTE_ADDR')}")
                
                # LOCKOUT: Dupa 5 incercari esuate
                if failed_attempts >= 5:
                    cache.set(lockout_key, True, timeout=900)  # 15 minute lockout
                    logger.error(f"User {user.username} locked out due to 5 failed 2FA attempts from IP {request.META.get('REMOTE_ADDR')}")
                    
                    return Response({
                        'error': 'Too many failed attempts. Account locked for 15 minutes.'
                    }, status=status.HTTP_429_TOO_MANY_REQUESTS)
                
                return Response({
                    'error': f'Invalid 2FA code. {5 - failed_attempts} attempts remaining.'
                }, status=status.HTTP_401_UNAUTHORIZED)
                
        except (User.DoesNotExist, TOTPDevice.DoesNotExist):
            # LOG: Attempted access with invalid user/device
            import logging
            logger = logging.getLogger(__name__)
            logger.error(f"2FA attempt with invalid user_id {user_id} from IP {request.META.get('REMOTE_ADDR')}")

            return Response({'error': 'Invalid request'}, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=False, methods=['post'], permission_classes=[permissions.AllowAny])
    def verify_backup_code(self, request):
        """Authenticate a user using a backup code."""
        user_id = request.data.get('user_id')
        code = request.data.get('code')

        if not user_id or not code:
            return Response(
                {'error': 'User ID and code are required'},
                status=status.HTTP_400_BAD_REQUEST,
            )

        try:
            user = User.objects.get(id=user_id)
            profile = UserProfile.objects.get(user=user)
        except (User.DoesNotExist, UserProfile.DoesNotExist):
            return Response({'error': 'Invalid request'}, status=status.HTTP_400_BAD_REQUEST)

        if not profile.verify_backup_code(code):
            return Response({'error': 'Invalid backup code'}, status=status.HTTP_401_UNAUTHORIZED)

        Token.objects.filter(user=user).delete()
        token = Token.objects.create(user=user)

        doctor_id = None
        patient_id = None

        if profile.role == 'doctor' and hasattr(user, 'doctor'):
            doctor_id = user.doctor.id
        elif profile.role == 'patient' and hasattr(user, 'patient'):
            patient_id = user.patient.id

        response = Response(
            {
                'user_id': user.id,
                'email': user.email,
                'role': profile.role,
                'first_name': user.first_name,
                'last_name': user.last_name,
                'doctor_id': doctor_id,
                'patient_id': patient_id,
                'two_fa_enabled': profile.two_fa_enabled,
                'token': token.key,
            },
            status=status.HTTP_200_OK,
        )
        secure = not getattr(settings, 'DEBUG', False)
        response.set_cookie(
            'refresh_token',
            token.key,
            httponly=True,
            secure=secure,
            samesite='Strict',
        )
        return response
    
    @action(detail=False, methods=['get'], permission_classes=[permissions.IsAuthenticated])
    def get_2fa_status(self, request):
        user = request.user
        profile = UserProfile.objects.get(user=user)
        
        return Response({
            'two_fa_enabled': profile.two_fa_enabled,
            'has_totp_device': TOTPDevice.objects.filter(user=user, confirmed=True).exists()
        }, status=status.HTTP_200_OK)

    @action(detail=False, methods=['get'], permission_classes=[permissions.IsAuthenticated])
    def get_profile(self, request):
        """Get current user's complete profile"""
        user = request.user
        profile = UserProfile.objects.get(user=user)
        
        # Base user data
        profile_data = {
            'id': user.id,
            'username': user.username,
            'email': user.email,
            'first_name': user.first_name,
            'last_name': user.last_name,
            'phone_number': profile.phone_number,
            'role': profile.role,
            'two_fa_enabled': profile.two_fa_enabled,
            'last_login': user.last_login.isoformat() if user.last_login else None,
            'date_joined': user.date_joined.isoformat(),
        }
        
        # Role-specific data
        if profile.role == 'doctor' and hasattr(user, 'doctor'):
            profile_data.update({
                'speciality': user.doctor.speciality,
                'description': user.doctor.description,
                'doctor_id': user.doctor.id
            })
        elif profile.role == 'patient' and hasattr(user, 'patient'):
            profile_data.update({
                'date_of_birth': user.patient.date_of_birth.isoformat() if user.patient.date_of_birth else None,
                'patient_id': user.patient.id
            })
        
        return Response(profile_data, status=status.HTTP_200_OK)

    @action(detail=False, methods=['put'], permission_classes=[permissions.IsAuthenticated])
    def update_profile(self, request):
        """Update current user's profile"""
        user = request.user
        profile = UserProfile.objects.get(user=user)
        
        try:
            with transaction.atomic():
                # Update basic user info
                user.first_name = request.data.get('first_name', user.first_name)
                user.last_name = request.data.get('last_name', user.last_name)
                # Note: email cannot be changed for security reasons
                user.save()
                
                # Update profile info
                profile.phone_number = request.data.get('phone_number', profile.phone_number)
                profile.save()
                
                # Update role-specific info
                if profile.role == 'doctor' and hasattr(user, 'doctor'):
                    doctor = user.doctor
                    doctor.speciality = request.data.get('speciality', doctor.speciality)
                    doctor.description = request.data.get('description', doctor.description)
                    doctor.save()
                
                elif profile.role == 'patient' and hasattr(user, 'patient'):
                    patient = user.patient
                    date_of_birth = request.data.get('date_of_birth')
                    if date_of_birth:
                        try:
                            from datetime import datetime
                            patient.date_of_birth = datetime.fromisoformat(date_of_birth.replace('Z', '+00:00')).date()
                        except ValueError:
                            # Try parsing as date only
                            patient.date_of_birth = datetime.strptime(date_of_birth, '%Y-%m-%d').date()
                    patient.save()
                
                # Return updated profile
                return self.get_profile(request)
                
        except Exception as e:
            return Response(
                {'error': f'Failed to update profile: {str(e)}'}, 
                status=status.HTTP_400_BAD_REQUEST
            )

    @action(detail=False, methods=['post'], permission_classes=[permissions.IsAuthenticated])
    def change_password(self, request):
        """Change user password"""
        user = request.user
        current_password = request.data.get('current_password')
        new_password = request.data.get('new_password')
        
        if not current_password or not new_password:
            return Response(
                {'error': 'Both current and new password are required'}, 
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Verify current password
        if not user.check_password(current_password):
            return Response(
                {'error': 'Current password is incorrect'}, 
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Validate new password
        from django.contrib.auth.password_validation import validate_password
        from django.core.exceptions import ValidationError
        
        try:
            validate_password(new_password, user)
        except ValidationError as e:
            return Response(
                {'error': list(e.messages)}, 
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Update password
        user.set_password(new_password)
        user.save()
        
        # Invalidate all existing sessions/tokens for security
        from rest_framework.authtoken.models import Token
        Token.objects.filter(user=user).delete()
        
        # Create new token and set cookie
        new_token = Token.objects.create(user=user)

        response = Response(
            {'message': 'Password changed successfully'},
            status=status.HTTP_200_OK,
        )

        secure = not getattr(settings, 'DEBUG', False)
        response.set_cookie(
            'refresh_token',
            new_token.key,
            httponly=True,
            secure=secure,
            samesite='Strict',
        )

        return response

    @action(detail=False, methods=['get'], permission_classes=[permissions.IsAuthenticated])
    def get_notification_preferences(self, request):
        """Get user's notification preferences"""
        user = request.user
        
        # Get or create notification preferences
        preferences, created = NotificationPreferences.objects.get_or_create(
            user=user,
            defaults={
                'email_enabled': True,
                'appointment_confirmations': True,
                'appointment_reminders': True,
                'appointment_cancellations': True,
                'system_notifications': True,
                'status_updates': True,
                'reminder_hours_before': 24,
            }
        )
        
        serializer = NotificationPreferencesSerializer(preferences)
        return Response(serializer.data, status=status.HTTP_200_OK)

    @action(detail=False, methods=['put'], permission_classes=[permissions.IsAuthenticated])
    def update_notification_preferences(self, request):
        """Update user's notification preferences"""
        user = request.user
        
        try:
            # Get or create preferences
            preferences, created = NotificationPreferences.objects.get_or_create(
                user=user,
                defaults={
                    'email_enabled': True,
                    'appointment_confirmations': True,
                    'appointment_reminders': True,
                    'appointment_cancellations': True,
                    'system_notifications': True,
                    'status_updates': True,
                    'reminder_hours_before': 24,
                }
            )
            
            # Update with provided data
            serializer = NotificationPreferencesSerializer(preferences, data=request.data, partial=True)
            
            if serializer.is_valid():
                serializer.save()
                return Response(serializer.data, status=status.HTTP_200_OK)
            else:
                return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
                
        except Exception as e:
            return Response(
                {'error': f'Failed to update notification preferences: {str(e)}'}, 
                status=status.HTTP_400_BAD_REQUEST
            )

    @action(detail=False, methods=['post'], permission_classes=[permissions.IsAuthenticated])
    def reset_notification_preferences(self, request):
        """Reset notification preferences to defaults"""
        user = request.user
        
        try:
            preferences, created = NotificationPreferences.objects.get_or_create(user=user)
            
            # Reset to defaults
            preferences.email_enabled = True
            preferences.appointment_confirmations = True
            preferences.appointment_reminders = True
            preferences.appointment_cancellations = True
            preferences.system_notifications = True
            preferences.status_updates = True
            preferences.reminder_hours_before = 24
            preferences.save()
            
            serializer = NotificationPreferencesSerializer(preferences)
            return Response({
                'message': 'Notification preferences reset to defaults',
                'preferences': serializer.data
            }, status=status.HTTP_200_OK)
            
        except Exception as e:
            return Response(
                {'error': f'Failed to reset preferences: {str(e)}'}, 
                status=status.HTTP_400_BAD_REQUEST
            )

    @action(detail=True, methods=['put'], permission_classes=[IsAdminRole])
    def update_user_by_admin(self, request, pk=None):
        """
        Permite adminilor sa actualizeze informatiile unui utilizator
        """
        try:
            user = User.objects.get(pk=pk)
        except User.DoesNotExist:
            return Response({'error': 'User not found'}, status=status.HTTP_404_NOT_FOUND)

        serializer = AdminUserUpdateSerializer(instance=user, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save()

        logger = logging.getLogger(__name__)
        logger.info(f"Admin {request.user.username} updated user {user.username}")

        profile = user.profile
        user_data = {
            'id': user.id,
            'username': user.username,
            'email': user.email,
            'first_name': user.first_name,
            'last_name': user.last_name,
            'phone_number': profile.phone_number,
            'role': profile.role,
            'is_active': user.is_active,
            'date_joined': user.date_joined.isoformat(),
            'last_login': user.last_login.isoformat() if user.last_login else None,
        }

        if profile.role == 'doctor' and hasattr(user, 'doctor'):
            user_data.update({
                'speciality': user.doctor.speciality,
                'description': user.doctor.description,
            })
        elif profile.role == 'patient' and hasattr(user, 'patient'):
            user_data.update({
                'date_of_birth': user.patient.date_of_birth.isoformat() if user.patient.date_of_birth else None,
            })

        return Response(user_data, status=status.HTTP_200_OK)

    @action(detail=True, methods=['post'], permission_classes=[IsAdminRole])
    def reset_password_by_admin(self, request, pk=None):
        """
        Permite adminilor sa reseteze parola unui utilizator
        """
        try:
            user = User.objects.get(pk=pk)
        except User.DoesNotExist:
            return Response({'error': 'User not found'}, status=status.HTTP_404_NOT_FOUND)

        import string
        alphabet = string.ascii_letters + string.digits + "!@#$%&*"
        temp_password = ''.join(secrets.choice(alphabet) for _ in range(12))

        user.set_password(temp_password)
        user.save()

        logger = logging.getLogger(__name__)
        logger.info(f"Admin {request.user.username} reset password for user {user.username}")

        from django.core.mail import send_mail
        send_mail(
            subject='Password Reset',
            message=f'Your temporary password is: {temp_password}',
            from_email=None,
            recipient_list=[user.email],
            fail_silently=True,
        )

        return Response({
            'message': 'Password reset email sent',
            'user_email': user.email,
            'note': 'The user should change this password on first login'
        }, status=status.HTTP_200_OK)

    @action(detail=True, methods=['post'], permission_classes=[IsAdminRole])
    def deactivate_user(self, request, pk=None):
        """
        Permite adminilor sa dezactiveze/activeze utilizatori
        """
        try:
            user = User.objects.get(pk=pk)
        except User.DoesNotExist:
            return Response({'error': 'User not found'}, status=status.HTTP_404_NOT_FOUND)
        
        # Nu permite adminilor sa se dezactiveze pe ei insisi
        if user == request.user:
            return Response(
                {'error': 'You cannot deactivate your own account'}, 
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Toggle status-ul
        user.is_active = not user.is_active
        user.save()
        
        # Daca utilizatorul este dezactivat, sterge toate token-urile sale
        if not user.is_active:
            from rest_framework.authtoken.models import Token
            Token.objects.filter(user=user).delete()
        
        logger = logging.getLogger(__name__)
        action = "activated" if user.is_active else "deactivated"
        logger.info(f"Admin {request.user.username} {action} user {user.username}")
        
        return Response({
            'message': f'User {"activated" if user.is_active else "deactivated"} successfully',
            'user_id': user.id,
            'username': user.username,
            'is_active': user.is_active
        }, status=status.HTTP_200_OK)

    @action(detail=False, methods=['get'], permission_classes=[IsAdminRole])
    def get_all_users_for_admin(self, request):
        """
        Returneaza toti utilizatorii pentru admin dashboard
        """
        users = User.objects.select_related('profile').all().order_by('-date_joined')

        paginator = UserPagination()
        page = paginator.paginate_queryset(users, request)

        users_data = []
        for user in page:
            try:
                profile = user.profile
                user_data = {
                    'id': user.id,
                    'username': user.username,
                    'email': user.email,
                    'first_name': user.first_name,
                    'last_name': user.last_name,
                    'phone_number': profile.phone_number,
                    'role': profile.role,
                    'is_active': user.is_active,
                    'date_joined': user.date_joined.isoformat(),
                    'last_login': user.last_login.isoformat() if user.last_login else None,
                    'two_fa_enabled': profile.two_fa_enabled,
                }
                
                # Adauga informatii specifice rolului
                if profile.role == 'doctor' and hasattr(user, 'doctor'):
                    user_data.update({
                        'speciality': user.doctor.speciality,
                        'description': user.doctor.description,
                    })
                elif profile.role == 'patient' and hasattr(user, 'patient'):
                    user_data.update({
                        'date_of_birth': user.patient.date_of_birth.isoformat() if user.patient.date_of_birth else None,
                    })
                
                users_data.append(user_data)
                
            except UserProfile.DoesNotExist:
                # Skip users without profiles
                continue
        
        return paginator.get_paginated_response(users_data)
