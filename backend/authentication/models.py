from django.db import models
from django.contrib.auth.models import User
from django.contrib.auth.hashers import check_password

class UserProfile(models.Model):
    USER_ROLES = (
        ('patient', 'Patient'),
        ('doctor', 'Doctor'),
        ('admin', 'Admin'),
    )
    
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
    phone_number = models.CharField(max_length=15, blank=True, null=True)
    two_fa_enabled = models.BooleanField(default=False)
    backup_codes = models.JSONField(default=list, blank=True)
    role = models.CharField(max_length=10, choices=USER_ROLES, default='patient')

    def __str__(self):
        return f"{self.user.username}'s profile - {self.role}"

    def verify_backup_code(self, code: str) -> bool:
        """Validate a backup code and invalidate it if used.

        Args:
            code (str): The plaintext backup code supplied by the user.

        Returns:
            bool: True if the code is valid and has been invalidated, False otherwise.
        """
        for hashed_code in list(self.backup_codes):
            if check_password(code, hashed_code):
                self.backup_codes.remove(hashed_code)
                self.save(update_fields=["backup_codes"])
                return True
        return False

class NotificationPreferences(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='notification_preferences')
    
    # Email notifications
    email_enabled = models.BooleanField(default=True, help_text="Receive notifications via email")
    appointment_confirmations = models.BooleanField(default=True, help_text="Email when appointments are confirmed")
    appointment_reminders = models.BooleanField(default=True, help_text="Email reminders before appointments")
    appointment_cancellations = models.BooleanField(default=True, help_text="Email when appointments are cancelled")
    
    # System notifications
    system_notifications = models.BooleanField(default=True, help_text="Show in-app notifications")
    status_updates = models.BooleanField(default=True, help_text="Notifications for status changes")
    
    # Timing preferences
    reminder_hours_before = models.IntegerField(default=24, help_text="Hours before appointment to send reminder")
    
    # Marketing (optional)
    marketing_emails = models.BooleanField(default=False, help_text="Receive promotional emails")
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f"Notification preferences for {self.user.username}"
    
    class Meta:
        verbose_name = "Notification Preferences"
        verbose_name_plural = "Notification Preferences"