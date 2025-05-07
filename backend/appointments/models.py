from django.db import models
from doctors.models import Doctor, Schedule
from patients.models import Patient
from django.core.exceptions import ValidationError
from django.db import transaction

# Create your models here.
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
        unique_together = ('schedule', 'status')
    
    def __str__(self):
        return f"Appointment: {self.patient} with {self.doctor} on {self.schedule.date}"
    
    def clean(self):
        # Verifica daca programul este disponibil
        if not self.schedule.is_available and self.status != 'cancelled':
            raise ValidationError('This schedule is not available.')
    
    @transaction.atomic
    def save(self, *args, **kwargs):
        # Implementam controlul tranzactiilor aici
        # Blocam programul cand se face o programare
        if self.status in ['pending', 'confirmed']:
            self.schedule.is_available = False
            self.schedule.save()
        elif self.status == 'cancelled':
            self.schedule.is_available = True
            self.schedule.save()
        
        super().save(*args, **kwargs)
