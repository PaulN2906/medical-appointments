from rest_framework import serializers
from .models import Patient
from authentication.serializers import UserSerializer

class PatientSerializer(serializers.ModelSerializer):
    user = UserSerializer(read_only=True)
    
    class Meta:
        model = Patient
        fields = ['id', 'user', 'date_of_birth']
        read_only_fields = ['id']
