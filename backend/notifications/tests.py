from django.contrib.auth.models import User
from rest_framework.test import APITestCase, APIClient
from unittest.mock import patch

from .models import Notification


class NotificationTests(APITestCase):
    def setUp(self):
        self.user = User.objects.create_user(username="u", password="p")
        self.client = APIClient()
        self.client.force_authenticate(user=self.user)

    @patch("notifications.email_service.EmailService.send_notification_email", return_value=True)
    def test_email_sent_on_create(self, mock_send):
        notification = Notification.objects.create(
            user=self.user,
            type="email",
            title="Hello",
            message="World",
        )
        notification.refresh_from_db()
        self.assertTrue(notification.email_sent)
        self.assertIsNotNone(notification.email_sent_at)
        mock_send.assert_called_once()

    def test_mark_as_read_action(self):
        notification = Notification.objects.create(
            user=self.user,
            type="system",
            title="Hello",
            message="World",
        )
        url = f"/api/notifications/notifications/{notification.id}/mark_as_read/"
        response = self.client.post(url)
        self.assertEqual(response.status_code, 200)
        notification.refresh_from_db()
        self.assertTrue(notification.read)

    def test_user_field_is_read_only(self):
        other = User.objects.create_user(username="other", password="p")
        data = {
            "user": other.id,
            "type": "system",
            "title": "Hi",
            "message": "There",
        }
        response = self.client.post("/api/notifications/notifications/", data)
        self.assertEqual(response.status_code, 201)
        notif = Notification.objects.get(id=response.data["id"])
        self.assertEqual(notif.user, self.user)

    def test_mark_all_as_read(self):
        Notification.objects.create(user=self.user, type="system", title="1", message="m")
        Notification.objects.create(user=self.user, type="system", title="2", message="m")
        url = "/api/notifications/notifications/mark_all_as_read/"
        response = self.client.post(url)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(Notification.objects.filter(user=self.user, read=True).count(), 2)

    @patch("notifications.email_service.EmailService.send_notification_email", return_value=True)
    def test_send_email_action_updates_flags(self, mock_send):
        notif = Notification.objects.create(
            user=self.user,
            type="email",
            title="T",
            message="M",
        )
        mock_send.reset_mock()
        url = f"/api/notifications/notifications/{notif.id}/send_email/"
        response = self.client.post(url)
        self.assertEqual(response.status_code, 200)
        notif.refresh_from_db()
        self.assertTrue(notif.email_sent)
        self.assertIsNotNone(notif.email_sent_at)
        mock_send.assert_called_once_with(notif)
