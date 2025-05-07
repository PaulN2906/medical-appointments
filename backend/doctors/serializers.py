from rest_framework import serializers
from .models import Doctor, Schedule
from authentication.serializers import UserSerializer

class DoctorSerializer(serializers.ModelSerializer):
    user = UserSerializer(read_only=True)
    
    class Meta:
        model = Doctor
        fields = ['id', 'user', 'speciality', 'description']
        read_only_fields = ['id']

class ScheduleSerializer(serializers.ModelSerializer):
    doctor_name = serializers.SerializerMethodField()
    
    class Meta:
        model = Schedule
        fields = ['id', 'doctor', 'doctor_name', 'date', 'start_time', 'end_time', 'is_available']
        read_only_fields = ['id']
    
    def get_doctor_name(self, obj):
        return f"Dr. {obj.doctor.user.last_name} {obj.doctor.user.first_name}"
