from django.db import models
from django.contrib.auth.models import User

# Create your models here.
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
    
    def __str__(self):
        return f"{self.title} to {self.user.username}"
