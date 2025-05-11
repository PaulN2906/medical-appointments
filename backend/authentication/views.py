from rest_framework import viewsets, status, permissions
from rest_framework.response import Response
from rest_framework.decorators import action
from django.contrib.auth.models import User
from .models import UserProfile
from .serializers import UserSerializer, UserProfileSerializer
from django.contrib.auth import authenticate
from rest_framework.authtoken.models import Token
from django_otp.plugins.otp_totp.models import TOTPDevice
import pyotp

class UserViewSet(viewsets.ModelViewSet):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    @action(detail=False, methods=['post'], permission_classes=[permissions.AllowAny])
    def register(self, request):
        serializer = UserSerializer(data=request.data)
        if serializer.is_valid():
            user = serializer.save()  # aici parola e deja criptata
            UserProfile.objects.create(user=user)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    @action(detail=False, methods=['post'], permission_classes=[permissions.AllowAny])
    def login(self, request):
        username = request.data.get('username')
        password = request.data.get('password')
        
        user = authenticate(username=username, password=password)
        
        if user is not None:
            # Verificare daca 2FA este activat
            profile = UserProfile.objects.get(user=user)
            if profile.two_fa_enabled:
                return Response({
                    'message': '2FA required',
                    'user_id': user.id,
                    'requires_2fa': True
                }, status=status.HTTP_200_OK)
            
            # Daca 2FA nu este activat, genereaza token direct
            token, _ = Token.objects.get_or_create(user=user)
            return Response({
                'token': token.key,
                'user_id': user.id,
                'email': user.email,
                'requires_2fa': False
            }, status=status.HTTP_200_OK)
        else:
            return Response({'error': 'Invalid credentials'}, status=status.HTTP_401_UNAUTHORIZED)
    
    @action(detail=False, methods=['post'], permission_classes=[permissions.IsAuthenticated])
    def enable_2fa(self, request):
        user = request.user
        profile = UserProfile.objects.get(user=user)
        
        # Genereaza o cheie secreta pentru TOTP
        key = pyotp.random_base32()
        
        # Creeaza sau actualizeaza dispozitivul TOTP
        device, created = TOTPDevice.objects.get_or_create(
            user=user,
            defaults={'name': f"{user.username}'s device", 'confirmed': True}
        )
        device.key = key
        device.save()
        
        profile.two_fa_enabled = True
        profile.save()
        
        # Genereaza un URL pentru configurarea aplicatiei de autentificare
        totp_url = pyotp.totp.TOTP(key).provisioning_uri(
            name=user.email,
            issuer_name="MedicalAppointments"
        )
        
        return Response({
            'message': '2FA has been enabled',
            'key': key,
            'totp_url': totp_url
        }, status=status.HTTP_200_OK)
    
    @action(detail=False, methods=['post'], permission_classes=[permissions.AllowAny])
    def verify_2fa(self, request):
        user_id = request.data.get('user_id')
        code = request.data.get('code')
        
        try:
            user = User.objects.get(id=user_id)
            device = TOTPDevice.objects.get(user=user)
            
            totp = pyotp.TOTP(device.key)
            if totp.verify(code):
                token, _ = Token.objects.get_or_create(user=user)
                return Response({
                    'token': token.key,
                    'user_id': user.id,
                    'email': user.email,
                }, status=status.HTTP_200_OK)
            else:
                return Response({'error': 'Invalid 2FA code'}, status=status.HTTP_401_UNAUTHORIZED)
        except (User.DoesNotExist, TOTPDevice.DoesNotExist):
            return Response({'error': 'User or device not found'}, status=status.HTTP_404_NOT_FOUND)
