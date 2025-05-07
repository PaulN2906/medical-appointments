from rest_framework import serializers
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
