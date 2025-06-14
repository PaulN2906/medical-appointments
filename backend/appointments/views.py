from rest_framework import viewsets, permissions, status
from rest_framework.response import Response
from rest_framework.decorators import action
from django.db import transaction, IntegrityError
from django.core.exceptions import PermissionDenied, ValidationError
from django.shortcuts import get_object_or_404
from .models import Appointment
from .serializers import AppointmentSerializer
from doctors.models import Schedule
from notifications.models import Notification
import logging
import time

logger = logging.getLogger(__name__)

class AppointmentViewSet(viewsets.ModelViewSet):
    queryset = Appointment.objects.all()
    serializer_class = AppointmentSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        user = self.request.user
        
        # Verifica explicit rolul utilizatorului
        if hasattr(user, 'doctor') and user.doctor:
            # Doctorul vede doar appointment-urile sale
            return Appointment.objects.filter(doctor=user.doctor)
        elif hasattr(user, 'patient') and user.patient:
            # Pacientul vede doar appointment-urile sale
            return Appointment.objects.filter(patient=user.patient)
        elif user.is_staff or user.is_superuser:
            # Admin-ul vede toate appointment-urile
            return Appointment.objects.all()
        else:
            # Utilizatori fara rol valid nu vad nimic
            return Appointment.objects.none()
        
    def get_object(self):
        """
        Returneaza appointment-ul doar daca utilizatorul are dreptul sa-l acceseze
        """
        obj = get_object_or_404(Appointment, pk=self.kwargs['pk'])
        
        user = self.request.user
        
        # Verifica dacă utilizatorul are dreptul sa acceseze acest appointment
        if hasattr(user, 'doctor') and user.doctor:
            if obj.doctor != user.doctor:
                raise PermissionDenied("You can only access your own appointments as a doctor.")
        elif hasattr(user, 'patient') and user.patient:
            if obj.patient != user.patient:
                raise PermissionDenied("You can only access your own appointments as a patient.")
        elif not (user.is_staff or user.is_superuser):
            raise PermissionDenied("You don't have permission to access this appointment.")
        
        return obj
    
    def create(self, request, *args, **kwargs):
        """
        SQLite-compatible appointment creation with proper transaction control
        Demonstrates ACID properties and conflict resolution
        """
        schedule_id = request.data.get('schedule')
        
        try:
            schedule = Schedule.objects.get(id=schedule_id)
        except Schedule.DoesNotExist:
            return Response(
                {'error': 'Schedule not found'},
                status=status.HTTP_404_NOT_FOUND
            )
        
        # Log the booking attempt for thesis demonstration
        logger.info(f"Appointment booking attempt for schedule {schedule_id} by user {request.user.id}")
        
        try:
            # Use the retry mechanism for SQLite transaction control
            serializer = self.get_serializer(data=request.data)
            serializer.is_valid(raise_exception=True)
            
            # Extract data for appointment creation
            appointment_data = {
                'patient': serializer.validated_data['patient'],
                'doctor': serializer.validated_data['doctor'], 
                'schedule': serializer.validated_data['schedule'],
                'notes': serializer.validated_data.get('notes', ''),
                'status': 'pending'
            }
            
            # Use the retry mechanism from the model
            appointment = Appointment.create_with_retry(**appointment_data)
            
            # Create notification for doctor
            from django.utils.html import escape
            safe_first_name = escape(appointment.patient.user.first_name)
            safe_last_name = escape(appointment.patient.user.last_name)

            Notification.objects.create(
                user=appointment.doctor.user,
                type='system',
                title='New Appointment',
                message=f'You have a new appointment with {safe_first_name} {safe_last_name} on {appointment.schedule.date} at {appointment.schedule.start_time}'
            )
            
            # Log successful booking
            logger.info(f"Appointment {appointment.id} successfully created for schedule {schedule_id}")
            
            # Return serialized appointment
            response_serializer = self.get_serializer(appointment)
            return Response(response_serializer.data, status=status.HTTP_201_CREATED)
            
        except ValidationError as e:
            logger.warning(f"Appointment booking failed for schedule {schedule_id}: {str(e)}")
            return Response(
                {'error': str(e)},
                status=status.HTTP_400_BAD_REQUEST
            )
        except IntegrityError as e:
            logger.warning(f"Appointment booking conflict for schedule {schedule_id}: {str(e)}")
            return Response(
                {'error': 'This schedule slot is no longer available'},
                status=status.HTTP_409_CONFLICT
            )
        except Exception as e:
            logger.error(f"Unexpected error in appointment booking for schedule {schedule_id}: {str(e)}")
            return Response(
                {'error': 'Unable to create appointment. Please try again.'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
    
    @action(detail=True, methods=['post'])
    @transaction.atomic
    def confirm(self, request, pk=None):
        appointment = self.get_object()
        
        if appointment.status != 'pending':
            return Response(
                {'error': 'Only pending appointments can be confirmed'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        appointment.status = 'confirmed'
        appointment.save()
        
        from django.utils.html import escape
        safe_doctor_name = escape(appointment.doctor.user.last_name)

        # Cream notificare pentru pacient
        Notification.objects.create(
            user=appointment.patient.user,
            type='email',
            title='Appointment Confirmed',
            message=f'Your appointment with Dr. {safe_doctor_name} on {appointment.schedule.date} at {appointment.schedule.start_time} has been confirmed.'
        )
        
        logger.info(f"Appointment {appointment.id} confirmed by user {request.user.id}")
        return Response({'status': 'appointment confirmed'})
    
    @action(detail=True, methods=['post'])
    @transaction.atomic
    def cancel(self, request, pk=None):
        appointment = self.get_object()
        
        if appointment.status in ['completed', 'cancelled']:
            return Response(
                {'error': 'This appointment cannot be cancelled'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Salveaza ID-ul schedule-ului inainte de a schimba status-ul
        schedule = appointment.schedule
        
        appointment.status = 'cancelled'
        appointment.save()  # This will handle schedule availability update
        
        from django.utils.html import escape
        
        # Notificam celalalt participant
        if request.user == appointment.doctor.user:
            # Medicul anuleaza
            safe_doctor_name = escape(appointment.doctor.user.last_name)
            Notification.objects.create(
                user=appointment.patient.user,
                type='email',
                title='Appointment Cancelled',
                message=f'Your appointment with Dr. {safe_doctor_name} on {appointment.schedule.date} has been cancelled.'
            )
        else:
            # Pacientul anuleaza
            safe_first_name = escape(appointment.patient.user.first_name)
            safe_last_name = escape(appointment.patient.user.last_name)
            Notification.objects.create(
                user=appointment.doctor.user,
                type='system',
                title='Appointment Cancelled',
                message=f'The appointment with {safe_first_name} {safe_last_name} on {appointment.schedule.date} has been cancelled.'
            )
        
        logger.info(f"Appointment {appointment.id} cancelled by user {request.user.id}")
        return Response({'status': 'appointment cancelled'})
