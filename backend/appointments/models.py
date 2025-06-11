from django.db import models, transaction, IntegrityError
from doctors.models import Doctor, Schedule
from patients.models import Patient
from django.core.exceptions import ValidationError
import time
import random

class Appointment(models.Model):
    STATUS_CHOICES = (
        ('pending', 'Pending'),
        ('confirmed', 'Confirmed'),
        ('cancelled', 'Cancelled'),
        ('completed', 'Completed'),
    )
    
    patient = models.ForeignKey(Patient, on_delete=models.CASCADE, related_name='appointments')
    doctor = models.ForeignKey(Doctor, on_delete=models.CASCADE, related_name='appointments')
    schedule = models.ForeignKey(Schedule, on_delete=models.CASCADE, related_name='appointments')
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    notes = models.TextField(blank=True, null=True)
    
    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=['schedule'],
                condition=models.Q(status__in=['pending', 'confirmed']),
                name='unique_active_appointment_per_schedule'
            )
        ]
    
    def __str__(self):
        return f"Appointment: {self.patient} with {self.doctor} on {self.schedule.date}"
    
    def clean(self):
        # Only prevent double booking
        if self.status in ['pending', 'confirmed']:
            existing = Appointment.objects.filter(
                schedule=self.schedule,
                status__in=['pending', 'confirmed']
            ).exclude(pk=self.pk)
            
            if existing.exists():
                raise ValidationError('This schedule slot is already booked.')
    
    @transaction.atomic
    def save(self, *args, **kwargs):
        """
        SQLite-compatible atomic save with retry logic for race conditions
        """
        # Update schedule availability based on appointment status
        if self.status in ['pending', 'confirmed']:
            # Use atomic transaction to prevent race conditions
            try:
                # Check if schedule is still available before booking
                schedule = Schedule.objects.get(id=self.schedule.id)
                if not schedule.is_available and not self.pk:
                    # New appointment on unavailable schedule
                    raise ValidationError('This schedule slot is no longer available.')
                
                # Save the appointment first
                super().save(*args, **kwargs)
                
                # Then update schedule availability
                schedule.is_available = False
                schedule.save()
                
            except IntegrityError:
                # Handle constraint violation (double booking attempt)
                raise ValidationError('This schedule slot is already booked.')
                
        elif self.status == 'cancelled':
            # Save the appointment first
            super().save(*args, **kwargs)
            
            # Check if there are other active appointments for this schedule
            other_active = Appointment.objects.filter(
                schedule=self.schedule,
                status__in=['pending', 'confirmed']
            ).exclude(pk=self.pk)
            
            if not other_active.exists():
                self.schedule.is_available = True
                self.schedule.save()
        else:
            # For other statuses, just save normally
            super().save(*args, **kwargs)

    @classmethod
    def create_with_retry(cls, **kwargs):
        """
        Create appointment with retry logic for SQLite race conditions
        Demonstrates transaction control and conflict resolution
        """
        max_retries = 3
        base_delay = 0.1  # 100ms
        
        for attempt in range(max_retries):
            try:
                with transaction.atomic():
                    # Verify schedule availability
                    schedule = Schedule.objects.get(id=kwargs['schedule'].id)
                    if not schedule.is_available:
                        raise ValidationError("Schedule slot is no longer available")
                    
                    # Create appointment
                    appointment = cls.objects.create(**kwargs)
                    
                    # Success - return the appointment
                    return appointment
                    
            except (IntegrityError, ValidationError) as e:
                if attempt == max_retries - 1:
                    # Last attempt failed
                    raise ValidationError(f"Unable to book appointment: {str(e)}")
                
                # Wait with exponential backoff before retry
                delay = base_delay * (2 ** attempt) + random.uniform(0, 0.1)
                time.sleep(delay)
                
                # Log the retry attempt
                import logging
                logger = logging.getLogger(__name__)
                logger.info(f"Appointment booking retry {attempt + 1}/{max_retries} after {delay:.3f}s")
        
        raise ValidationError("Unable to book appointment after maximum retries")
