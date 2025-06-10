from rest_framework import serializers
from datetime import date, datetime, time
from django.utils import timezone
from .models import Appointment
from doctors.serializers import DoctorSerializer, ScheduleSerializer
from patients.serializers import PatientSerializer

class AppointmentSerializer(serializers.ModelSerializer):
    doctor_details = DoctorSerializer(source='doctor', read_only=True)
    patient_details = PatientSerializer(source='patient', read_only=True)
    schedule_details = ScheduleSerializer(source='schedule', read_only=True)
    
    class Meta:
        model = Appointment
        fields = ['id', 'patient', 'doctor', 'schedule', 'doctor_details', 'patient_details', 
                  'schedule_details', 'status', 'created_at', 'updated_at', 'notes']
        read_only_fields = ['id', 'created_at', 'updated_at', 'doctor_details', 'patient_details', 'schedule_details']
    
    def validate_schedule(self, value):
        """
        Valideaza ca schedule-ul este valid pentru programare
        """
        # 1. Verifica daca schedule-ul exista si este disponibil
        if not value.is_available:
            raise serializers.ValidationError("This time slot is no longer available.")
        
        # 2. Verifica daca programarea nu este in trecut
        appointment_datetime = timezone.make_aware(
            datetime.combine(value.date, value.start_time),
            timezone.get_current_timezone()
        )
        now = timezone.now()
        
        if appointment_datetime <= now:
            raise serializers.ValidationError("Cannot book appointments in the past.")
        
        # 3. Verifica daca programarea nu este prea departe in viitor (6 luni)
        from datetime import timedelta
        max_future_date = now + timedelta(days=180)  # 6 luni
        if appointment_datetime > max_future_date:
            raise serializers.ValidationError("Cannot book appointments more than 6 months in advance.")
        
        # 4. Verifica zilele lucratoare (Luni-Vineri)
        if value.date.weekday() >= 5:  # 5=Sambata, 6=Duminica
            raise serializers.ValidationError("Appointments can only be booked on weekdays (Monday-Friday).")
        
        # 5. Verifica orele de program (8:00 - 18:00)
        business_start = time(8, 0)   # 8:00 AM
        business_end = time(18, 0)    # 6:00 PM
        
        if value.start_time < business_start or value.end_time > business_end:
            raise serializers.ValidationError("Appointments must be scheduled during business hours (8:00 AM - 6:00 PM).")
        
        # 6. Verifica daca programarea nu este prea aproape (minim 2 ore in avans)
        min_advance_time = now + timedelta(hours=2)
        if appointment_datetime < min_advance_time:
            raise serializers.ValidationError("Appointments must be booked at least 2 hours in advance.")
        
        return value
    
    def validate(self, data):
        """
        Validari la nivel de obiect
        """
        # Verifica daca pacientul nu are deja o programare in acelasi timp
        schedule = data.get('schedule')
        patient = data.get('patient')
        
        if schedule and patient:
            # Verifica overlap cu alte programari ale aceluiasi pacient
            existing_appointments = Appointment.objects.filter(
                patient=patient,
                schedule__date=schedule.date,
                status__in=['pending', 'confirmed']
            ).exclude(pk=self.instance.pk if self.instance else None)
            
            for existing in existing_appointments:
                # Verifica overlap de timp
                if (schedule.start_time < existing.schedule.end_time and 
                    schedule.end_time > existing.schedule.start_time):
                    raise serializers.ValidationError(
                        f"You already have an appointment on {schedule.date} "
                        f"from {existing.schedule.start_time} to {existing.schedule.end_time}."
                    )
        
        return data
