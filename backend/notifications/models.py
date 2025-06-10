import logging
from django.db import models
from django.contrib.auth.models import User
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.utils.html import escape

logger = logging.getLogger(__name__)

class Notification(models.Model):
    TYPE_CHOICES = (
        ('email', 'Email'),
        ('system', 'System Notification'),
    )
    
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='notifications')
    type = models.CharField(max_length=10, choices=TYPE_CHOICES)
    title = models.CharField(max_length=100)
    message = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    read = models.BooleanField(default=False)
    
    # New field for email tracking
    email_sent = models.BooleanField(default=False, help_text="Indicates if email was sent successfully")
    email_sent_at = models.DateTimeField(null=True, blank=True, help_text="Timestamp when email was sent")
    
    class Meta:
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.title} to {self.user.username}"

@receiver(post_save, sender=Notification)
def send_email_notification(sender, instance, created, **kwargs):
    """
    Signal to automatically send email when a notification with type='email' is created
    """
    # Only process newly created notifications with type='email' that haven't been sent yet
    if created and instance.type == 'email' and not instance.email_sent:
        # Import here to avoid circular imports
        from .email_service import EmailService
        from django.utils import timezone
        
        logger.info(f"Attempting to send email for notification {instance.id} to {instance.user.email}")
        
        # asiguram continutul impotriva XSS
        instance.title = escape(instance.title)
        instance.message = escape(instance.message)
        
        # Attempt to send email
        email_success = EmailService.send_notification_email(instance)
        
        # Update the notification record with email status
        if email_success:
            instance.email_sent = True
            instance.email_sent_at = timezone.now()
            logger.info(f"Email sent successfully for notification {instance.id}")
        else:
            instance.email_sent = False
            logger.error(f"Failed to send email for notification {instance.id}")
        
        # Save the updated status (use update to avoid triggering the signal again)
        Notification.objects.filter(id=instance.id).update(
            email_sent=instance.email_sent,
            email_sent_at=instance.email_sent_at,
            title=instance.title,      # salvam versiunea sigura
            message=instance.message   # salvam versiunea sigura
        )
