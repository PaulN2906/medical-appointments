from rest_framework import serializers
from .models import Notification

class NotificationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Notification
        fields = [
            'id',
            'user',
            'type',
            'title',
            'message',
            'created_at',
            'read',
            'email_sent',
            'email_sent_at',
        ]
        read_only_fields = ['id', 'created_at', 'user', 'email_sent', 'email_sent_at']
