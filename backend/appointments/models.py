from django.db import models
from doctors.models import Doctor, Schedule
from patients.models import Patient
from django.core.exceptions import ValidationError
from django.db import transaction

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
        # Update schedule availability based on appointment status
        if self.status in ['pending', 'confirmed']:
            self.schedule.is_available = False
            self.schedule.save()
        elif self.status == 'cancelled':
            # Check if there are other active appointments for this schedule
            other_active = Appointment.objects.filter(
                schedule=self.schedule,
                status__in=['pending', 'confirmed']
            ).exclude(pk=self.pk)
            
            if not other_active.exists():
                self.schedule.is_available = True
                self.schedule.save()
        
        super().save(*args, **kwargs)
