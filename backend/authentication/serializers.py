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
            'marketing_emails',
            'updated_at'
        ]
        read_only_fields = ['updated_at']
