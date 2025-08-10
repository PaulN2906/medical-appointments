from rest_framework import serializers
from django.contrib.auth.models import User
from django.core.validators import validate_email
from django.core.exceptions import ValidationError
from .models import UserProfile, NotificationPreferences

class UserSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True)

    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'first_name', 'last_name', 'password']
        read_only_fields = ['id']
    
    def validate_email(self, value):
        """
        Valideaza formatul email-ului
        """
        try:
            validate_email(value)
        except ValidationError:
            raise serializers.ValidationError("Enter a valid email address.")
        
        # Verifica daca email-ul nu este deja folosit
        if User.objects.filter(email=value).exclude(pk=self.instance.pk if self.instance else None).exists():
            raise serializers.ValidationError("A user with this email already exists.")
        
        return value.lower()  # Normalizeaza la lowercase

    def create(self, validated_data):
        password = validated_data.pop('password')
        user = User(**validated_data)
        user.set_password(password)
        user.save()
        return user


class AdminUserUpdateSerializer(serializers.ModelSerializer):
    phone_number = serializers.CharField(required=False, allow_blank=True)
    speciality = serializers.CharField(required=False, allow_blank=True)
    description = serializers.CharField(required=False, allow_blank=True)
    date_of_birth = serializers.DateField(required=False, allow_null=True)

    class Meta:
        model = User
        fields = [
            'first_name',
            'last_name',
            'email',
            'phone_number',
            'speciality',
            'description',
            'date_of_birth'
        ]

    def validate_email(self, value):
        try:
            validate_email(value)
        except ValidationError:
            raise serializers.ValidationError("Enter a valid email address.")

        if User.objects.filter(email=value).exclude(pk=self.instance.pk if self.instance else None).exists():
            raise serializers.ValidationError("A user with this email already exists.")

        return value.lower()

    def update(self, instance, validated_data):
        phone_number = validated_data.pop('phone_number', None)
        speciality = validated_data.pop('speciality', None)
        description = validated_data.pop('description', None)
        date_of_birth = validated_data.pop('date_of_birth', None)

        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()

        profile = instance.profile
        if phone_number is not None:
            profile.phone_number = phone_number
            profile.save()

        if profile.role == 'doctor' and hasattr(instance, 'doctor'):
            doctor = instance.doctor
            if speciality is not None:
                doctor.speciality = speciality
            if description is not None:
                doctor.description = description
            doctor.save()
        elif profile.role == 'patient' and hasattr(instance, 'patient'):
            patient = instance.patient
            if date_of_birth is not None:
                patient.date_of_birth = date_of_birth
                patient.save()

        return instance

class UserProfileSerializer(serializers.ModelSerializer):
    user = UserSerializer()
    
    class Meta:
        model = UserProfile
        fields = ['id', 'user', 'phone_number', 'two_fa_enabled']
        read_only_fields = ['id']
        
    def create(self, validated_data):
        user_data = validated_data.pop('user')
        user = User.objects.create_user(**user_data)
        return UserProfile.objects.create(user=user, **validated_data)

class NotificationPreferencesSerializer(serializers.ModelSerializer):
    class Meta:
        model = NotificationPreferences
        fields = [
            'email_enabled',
            'appointment_confirmations', 
            'appointment_reminders',
            'appointment_cancellations',
            'system_notifications',
            'status_updates',
            'reminder_hours_before',
            'updated_at'
        ]
        read_only_fields = ['updated_at']
