from django.db import models
from django.contrib.auth.models import User

class UserProfile(models.Model):
    USER_ROLES = (
        ('patient', 'Patient'),
        ('doctor', 'Doctor'),
        ('admin', 'Admin'),
    )
    
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
    phone_number = models.CharField(max_length=15, blank=True, null=True)
    two_fa_enabled = models.BooleanField(default=False)
    role = models.CharField(max_length=10, choices=USER_ROLES, default='patient')
    
    def __str__(self):
        return f"{self.user.username}'s profile - {self.role}"
