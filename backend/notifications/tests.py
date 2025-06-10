from django.test import TestCase
from django.contrib.auth.models import User
from .models import Notification


class NotificationModelTest(TestCase):
    def test_str_representation(self):
        user = User.objects.create_user(username='u', password='p')
        notification = Notification.objects.create(
            user=user,
            type='system',
            title='Hello',
            message='World'
        )
        self.assertEqual(str(notification), 'Hello to u')
