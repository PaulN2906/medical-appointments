from django.db.models.signals import post_save
from django.dispatch import receiver
from django.contrib.auth.models import User
from .models import UserProfile, NotificationPreferences

@receiver(post_save, sender=UserProfile)
def create_notification_preferences(sender, instance, created, **kwargs):
    """Automatically create notification preferences when a user profile is created"""
    if created:
        NotificationPreferences.objects.get_or_create(
            user=instance.user,
            defaults={
                'email_enabled': True,
                'appointment_confirmations': True,
                'appointment_reminders': True,
                'appointment_cancellations': True,
                'system_notifications': True,
                'status_updates': True,
                'reminder_hours_before': 24,
            }
        )
