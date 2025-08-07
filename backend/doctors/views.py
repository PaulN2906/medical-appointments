from rest_framework import viewsets, permissions, status
from rest_framework.response import Response
from rest_framework.decorators import action
from django.core.exceptions import PermissionDenied
from .models import Doctor, Schedule
from .serializers import DoctorSerializer, ScheduleSerializer
from django.db import transaction
from django.utils.decorators import method_decorator
from django.views.decorators.cache import cache_page
import logging

logger = logging.getLogger(__name__)

class DoctorViewSet(viewsets.ModelViewSet):
    queryset = Doctor.objects.all()
    serializer_class = DoctorSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        
        # Admins can see all doctors
        if user.is_staff or user.is_superuser:
            return Doctor.objects.all()
        
        if hasattr(user, 'profile') and user.profile.role =='admin':
            return Doctor.objects.all().select_related('user')
        
        # Doctors can see all doctors (but can only edit their own profile)
        if hasattr(user, "doctor"):
            return Doctor.objects.all()
        
        # Patients can see all doctors (read-only) for booking appointments
        if hasattr(user, "patient"):
            return Doctor.objects.all()
        
        # Fallback: no access for users without roles
        return Doctor.objects.none()

    def get_object(self):
        """
        Override to ensure doctors can only edit their own profile
        """
        obj = super().get_object()
        user = self.request.user
        
        # For non-safe methods (PUT, PATCH, DELETE), doctors can only edit themselves
        if self.request.method not in permissions.SAFE_METHODS:
            if hasattr(user, "doctor") and user.doctor != obj:
                raise PermissionDenied("You can only edit your own doctor profile.")
            elif hasattr(user, "patient"):
                raise PermissionDenied("Patients cannot edit doctor profiles.")
        
        return obj

    def perform_create(self, serializer):
        # Only allow admins to create new doctor profiles
        if not (self.request.user.is_staff or self.request.user.is_superuser):
            raise PermissionDenied("Only administrators can create doctor profiles.")
        serializer.save()

    def perform_update(self, serializer):
        # Doctors can only update their own profile
        user = self.request.user
        if hasattr(user, "doctor"):
            serializer.save()
        else:
            raise PermissionDenied("You can only update your own doctor profile.")

    def perform_destroy(self, instance):
        # Only admins can delete doctor profiles
        if not (self.request.user.is_staff or self.request.user.is_superuser):
            raise PermissionDenied("Only administrators can delete doctor profiles.")
        instance.delete()

class ScheduleViewSet(viewsets.ModelViewSet):
    queryset = Schedule.objects.all()
    serializer_class = ScheduleSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        
        # Admins can see all schedules
        if hasattr(user, 'profile') and user.profile.role == 'admin':
            return Schedule.objects.all().select_related('doctor__user')

        if user.is_staff or user.is_superuser:
            return Schedule.objects.all()
        
        # Doctors can see their own schedules
        if hasattr(user, "doctor"):
            return Schedule.objects.filter(doctor=user.doctor)
        
        # Patients can see all available schedules for booking
        if hasattr(user, "patient"):
            return Schedule.objects.filter(is_available=True)
        
        # Fallback: no access
        return Schedule.objects.none()
    
    # @method_decorator(cache_page(60*5))  # Cache for 5 minutes, disabled for now
    def list(self, request, *args, **kwargs):
        return super().list(request, *args, **kwargs)
    
    @transaction.atomic
    def create(self, request, *args, **kwargs):
        user = request.user
        
        # Admin poate crea schedule pentru orice doctor
        if hasattr(user, 'profile') and user.profile.role == 'admin':
            serializer = self.get_serializer(data=request.data)
            serializer.is_valid(raise_exception=True)
            
            # Pentru admin, doctor_id vine din request data
            doctor_id = request.data.get('doctor')
            if not doctor_id:
                return Response(
                    {'error': 'Doctor ID is required for admin schedule creation'},
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            try:
                doctor = Doctor.objects.get(id=doctor_id)
                serializer.save(doctor=doctor)
            except Doctor.DoesNotExist:
                return Response(
                    {'error': 'Doctor not found'},
                    status=status.HTTP_404_NOT_FOUND
                )
                
            headers = self.get_success_headers(serializer.data)
            return Response(
                serializer.data, status=status.HTTP_201_CREATED, headers=headers
            )
        
        # Pentru doctori normali
        if not hasattr(user, "doctor"):
            raise PermissionDenied("Only doctors can create schedules.")

        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save(doctor=user.doctor)
        headers = self.get_success_headers(serializer.data)
        return Response(
            serializer.data, status=status.HTTP_201_CREATED, headers=headers
        )

    def get_object(self):
        """
        Override to ensure doctors can only modify their own schedules
        """
        obj = super().get_object()
        user = self.request.user
        
        # For non-safe methods, doctors can only edit their own schedules
        if self.request.method not in permissions.SAFE_METHODS:
            if hasattr(user, "doctor") and user.doctor != obj.doctor:
                raise PermissionDenied("You can only modify your own schedules.")
            elif hasattr(user, "patient"):
                raise PermissionDenied("Patients cannot modify schedules.")
        
        return obj

    @action(detail=False, methods=['post'])
    @transaction.atomic
    def bulk_create(self, request, *args, **kwargs):
        """Create multiple schedules in a single transaction"""
        serializer = self.get_serializer(data=request.data, many=True)
        serializer.is_valid(raise_exception=True)
        self.perform_bulk_create(serializer)
        headers = self.get_success_headers(serializer.data)
        return Response(serializer.data, status=status.HTTP_201_CREATED, headers=headers)

    def perform_bulk_create(self, serializer):
        """
        Handle the bulk creation of schedules with proper permission checks
        This method is called by bulk_create action
        """
        user = self.request.user
        if not hasattr(user, "doctor"):
            raise PermissionDenied("Only doctors can create schedules.")

        # Save all schedules and assign to the requesting doctor
        serializer.save(doctor=user.doctor)

    def destroy(self, request, *args, **kwargs):
        """
        Sterge un schedule din calendar
        Doar adminii si doctorii pot sterge
        """
        schedule = self.get_object()
        user = request.user
        
        # Verifica permisiunile
        if hasattr(user, 'profile') and user.profile.role == 'admin':
            # Admin poate sterge orice schedule
            pass
        elif hasattr(user, 'doctor') and user.doctor == schedule.doctor:
            # Doctorul poate sterge doar propriile schedule
            pass
        else:
            raise PermissionDenied("You don't have permission to delete this schedule.")
        
        # Verifica daca schedule are programari active
        from appointments.models import Appointment
        active_appointments = Appointment.objects.filter(
            schedule=schedule,
            status__in=['pending', 'confirmed']
        )
        
        if active_appointments.exists():
            return Response(
                {'error': 'Cannot delete schedule with active appointments. Please cancel or reschedule the appointments first.'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Sterge schedule
        schedule_id = schedule.id
        schedule.delete()
        
        logger.info(f"Schedule {schedule_id} deleted by user {request.user.id}")
        
        return Response(
            {'message': f'Schedule {schedule_id} deleted successfully'},
            status=status.HTTP_204_NO_CONTENT
        )
