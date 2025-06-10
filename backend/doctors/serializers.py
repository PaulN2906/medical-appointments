from rest_framework import serializers
from datetime import date, datetime, time, timedelta
from .models import Doctor, Schedule
from authentication.serializers import UserSerializer

class DoctorSerializer(serializers.ModelSerializer):
    user = UserSerializer(read_only=True)
    
    class Meta:
        model = Doctor
        fields = ['id', 'user', 'speciality', 'description']
        read_only_fields = ['id', 'user']

class ScheduleSerializer(serializers.ModelSerializer):
    doctor_name = serializers.SerializerMethodField()
    
    class Meta:
        model = Schedule
        fields = ['id', 'doctor', 'doctor_name', 'date', 'start_time', 'end_time', 'is_available']
        read_only_fields = ['id']
    
    def get_doctor_name(self, obj):
        return f"Dr. {obj.doctor.user.last_name} {obj.doctor.user.first_name}"
    
    def validate_date(self, value):
        """
        Valideaza data schedule-ului
        """
        # Nu permite schedule-uri in trecut
        if value < date.today():
            raise serializers.ValidationError("Cannot create schedules in the past.")
        
        # Nu permite schedule-uri prea departe in viitor (1 an)
        max_future_date = date.today() + timedelta(days=365)
        if value > max_future_date:
            raise serializers.ValidationError("Cannot create schedules more than 1 year in advance.")
        
        # Verifica zilele lucratoare
        if value.weekday() >= 5:  # 5=Sambata, 6=Duminica
            raise serializers.ValidationError("Schedules can only be created for weekdays (Monday-Friday).")
        
        return value
    
    def validate_start_time(self, value):
        """
        Valideaza ora de inceput
        """
        business_start = time(8, 0)   # 8:00 AM
        business_end = time(18, 0)    # 6:00 PM
        
        if value < business_start or value >= business_end:
            raise serializers.ValidationError("Start time must be during business hours (8:00 AM - 6:00 PM).")
        
        return value
    
    def validate_end_time(self, value):
        """
        Valideaza ora de sfarsit
        """
        business_start = time(8, 0)   # 8:00 AM
        business_end = time(18, 0)    # 6:00 PM
        
        if value <= business_start or value > business_end:
            raise serializers.ValidationError("End time must be during business hours (8:00 AM - 6:00 PM).")
        
        return value
    
    def validate(self, data):
        """
        Validari la nivel de obiect pentru Schedule
        """
        start_time = data.get('start_time')
        end_time = data.get('end_time')
        
        # Verifica daca start_time < end_time
        if start_time and end_time and start_time >= end_time:
            raise serializers.ValidationError("Start time must be before end time.")
        
        # Verifica durata minima (30 minute)
        if start_time and end_time:
            duration = datetime.combine(date.today(), end_time) - datetime.combine(date.today(), start_time)
            if duration.total_seconds() < 1800:  # 30 minute = 1800 secunde
                raise serializers.ValidationError("Appointment slots must be at least 30 minutes long.")
        
        # Verifica durata maxima (4 ore)
        if start_time and end_time:
            duration = datetime.combine(date.today(), end_time) - datetime.combine(date.today(), start_time)
            if duration.total_seconds() > 14400:  # 4 ore = 14400 secunde
                raise serializers.ValidationError("Appointment slots cannot be longer than 4 hours.")
        
        # Verifica overlap cu alte schedule-uri ale aceluiasi doctor
        doctor = data.get('doctor')
        schedule_date = data.get('date')
        
        if doctor and schedule_date and start_time and end_time:
            existing_schedules = Schedule.objects.filter(
                doctor=doctor,
                date=schedule_date
            ).exclude(pk=self.instance.pk if self.instance else None)
            
            for existing in existing_schedules:
                # Verifica overlap de timp
                if (start_time < existing.end_time and end_time > existing.start_time):
                    raise serializers.ValidationError(
                        f"This time slot overlaps with an existing schedule "
                        f"from {existing.start_time} to {existing.end_time}."
                    )
        
        return data
