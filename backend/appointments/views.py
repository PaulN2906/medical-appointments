from rest_framework import viewsets, permissions, status
from rest_framework.response import Response
from rest_framework.decorators import action
from django.db import transaction, IntegrityError
from django.core.exceptions import PermissionDenied
from django.shortcuts import get_object_or_404
from .models import Appointment
from .serializers import AppointmentSerializer
from doctors.models import Schedule
from notifications.models import Notification

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
    
    @transaction.atomic
    def create(self, request, *args, **kwargs):
        schedule_id = request.data.get('schedule')
        
        try:
            # SQLite nu merge bine cu instructiunea select_for_update()
            # Am adaugat alte conditii care sa asigure unicitatea
            #schedule = Schedule.objects.select_for_update().get(id=schedule_id)

            schedule = Schedule.objects.get(id=schedule_id)
            
            try:
                # Create appointment
                response = super().create(request, *args, **kwargs)

                # Marcam ca indisponibil doar daca programarea a fost creata cu succes
                if response.status_code == status.HTTP_201_CREATED:
                    schedule.refresh_from_db()
                    schedule.is_available = False
                    schedule.save()
            
                # Create notification for doctor
                    appointment = Appointment.objects.get(id=response.data['id'])
                    Notification.objects.create(
                        user=appointment.doctor.user,
                        type='system',
                        title='New Appointment',
                        message=f'You have a new appointment with {appointment.patient.user.first_name} {appointment.patient.user.last_name} on {appointment.schedule.date} at {appointment.schedule.start_time}'
                    )
                
                return response
            
            except IntegrityError as e:
                # Constraint de unicitate care previne double-booking
                # Verificam din nou disponibilitatea pt un mesaj mai clar
                schedule.refresh_from_db()
                if not schedule.is_available:
                    return Response(
                        {'error': 'This schedule slot is no longer available'},
                        status=status.HTTP_400_BAD_REQUEST
                    )
                else:
                    # Alta problema de integritate
                    return Response(
                        {'error': 'Unable to create appointment. Please try again.'},
                        status=status.HTTP_400_BAD_REQUEST
                    )
        
        except Schedule.DoesNotExist:
            return Response(
                {'error': 'Schedule not found'},
                status=status.HTTP_404_NOT_FOUND
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
        
        # Cream notificare pentru pacient
        Notification.objects.create(
            user=appointment.patient.user,
            type='email',
            title='Appointment Confirmed',
            message=f'Your appointment with Dr. {appointment.doctor.user.last_name} on {appointment.schedule.date} at {appointment.schedule.start_time} has been confirmed.'
        )
        
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
        appointment.save()
        
        # Verificam daca mai sunt appointment-uri active pentru acest schedule
        other_active = Appointment.objects.filter(
            schedule=schedule,
            status__in=['pending', 'confirmed']
        ).exclude(pk=appointment.pk)
        
        if not other_active.exists():
            schedule.is_available = True
            schedule.save()
        
        # Notificam celalalt participant
        if request.user == appointment.doctor.user:
            # Medicul anuleaza
            Notification.objects.create(
                user=appointment.patient.user,
                type='email',
                title='Appointment Cancelled',
                message=f'Your appointment with Dr. {appointment.doctor.user.last_name} on {appointment.schedule.date} has been cancelled.'
            )
        else:
            # Pacientul anuleaza
            Notification.objects.create(
                user=appointment.doctor.user,
                type='system',
                title='Appointment Cancelled',
                message=f'The appointment with {appointment.patient.user.first_name} {appointment.patient.user.last_name} on {appointment.schedule.date} has been cancelled.'
            )
        
        return Response({'status': 'appointment cancelled'})
