from rest_framework import viewsets, permissions, status
from rest_framework.response import Response
from rest_framework.decorators import action
from django.db import transaction
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
        
        # Verifica daca utilizatorul este medic sau pacient
        try:
            doctor = user.doctor
            return Appointment.objects.filter(doctor=doctor)
        except:
            pass
        
        try:
            patient = user.patient
            return Appointment.objects.filter(patient=patient)
        except:
            pass
        
        # Daca e admin, returneaza toate programarile
        if user.is_staff:
            return Appointment.objects.all()
        
        return Appointment.objects.none()
    
    @transaction.atomic
    def create(self, request, *args, **kwargs):
        # Implementam logica de tranzactii pentru creare programare
        schedule_id = request.data.get('schedule')
        
        # Verificam daca programul este disponibil
        try:
            schedule = Schedule.objects.select_for_update().get(id=schedule_id)
            if not schedule.is_available:
                return Response(
                    {'error': 'This schedule is no longer available'},
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            # Marcam programul ca indisponibil
            schedule.is_available = False
            schedule.save()
            
            # Cream programarea
            response = super().create(request, *args, **kwargs)
            
            # Cream notificare pentru medic
            if response.status_code == status.HTTP_201_CREATED:
                appointment = Appointment.objects.get(id=response.data['id'])
                Notification.objects.create(
                    user=appointment.doctor.user,
                    type='system',
                    title='New Appointment',
                    message=f'You have a new appointment with {appointment.patient.user.first_name} {appointment.patient.user.last_name} on {appointment.schedule.date} at {appointment.schedule.start_time}'
                )
            
            return response
        
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
        
        appointment.status = 'cancelled'
        appointment.save()
        
        # Eliberam programul
        appointment.schedule.is_available = True
        appointment.schedule.save()
        
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
