from django.contrib.auth.models import User
from rest_framework.test import APITestCase, APIClient
from unittest.mock import patch
from django.utils import timezone
from datetime import timedelta, datetime

from .models import Notification
from .scheduler import dispatch_upcoming_appointment_reminders
from appointments.models import Appointment
from authentication.models import NotificationPreferences
from patients.models import Patient
from doctors.models import Doctor, Schedule


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


class AppointmentReminderSchedulerTests(APITestCase):
    def setUp(self):
        self.now = timezone.localtime(timezone.now()).replace(second=0, microsecond=0)
        self.patient_user = User.objects.create_user(username="patient", password="p")
        self.patient = Patient.objects.create(user=self.patient_user)
        self.doctor_user = User.objects.create_user(username="doctor", password="p")
        self.doctor = Doctor.objects.create(user=self.doctor_user, speciality="s")
        schedule_dt = self.now + timedelta(hours=24)
        start_time = schedule_dt.time().replace(tzinfo=None)
        end_time = (schedule_dt + timedelta(hours=1)).time().replace(tzinfo=None)
        self.schedule = Schedule.objects.create(
            doctor=self.doctor,
            date=schedule_dt.date(),
            start_time=start_time,
            end_time=end_time,
        )
        self.appointment = Appointment.objects.create(
            patient=self.patient,
            doctor=self.doctor,
            schedule=self.schedule,
            status="confirmed",
        )
        self.prefs = NotificationPreferences.objects.create(
            user=self.patient_user,
            email_enabled=True,
            appointment_reminders=True,
            reminder_hours_before=24,
        )

    @patch("notifications.scheduler.Notification.send_appointment_reminder")
    def test_skips_when_email_disabled(self, mock_send):
        self.prefs.email_enabled = False
        self.prefs.save()
        with patch("notifications.scheduler.timezone.now", return_value=self.now):
            dispatch_upcoming_appointment_reminders()
        mock_send.assert_not_called()
        self.appointment.refresh_from_db()
        self.assertFalse(self.appointment.reminder_sent)

    @patch("notifications.scheduler.Notification.send_appointment_reminder")
    def test_sends_when_enabled(self, mock_send):
        schedule_dt = datetime.combine(self.schedule.date, self.schedule.start_time)
        schedule_dt = timezone.make_aware(schedule_dt, timezone.get_current_timezone())
        reminder_time = schedule_dt - timedelta(hours=self.prefs.reminder_hours_before)
        self.assertEqual(reminder_time, self.now)
        with patch("notifications.scheduler.timezone.now", return_value=self.now):
            dispatch_upcoming_appointment_reminders()
        mock_send.assert_called_once_with(self.appointment)
        self.appointment.refresh_from_db()
        self.assertTrue(self.appointment.reminder_sent)

    @patch("notifications.scheduler.Notification.send_appointment_reminder")
    def test_sends_only_once(self, mock_send):
        schedule_dt = datetime.combine(self.schedule.date, self.schedule.start_time)
        schedule_dt = timezone.make_aware(schedule_dt, timezone.get_current_timezone())
        reminder_time = schedule_dt - timedelta(hours=self.prefs.reminder_hours_before)
        self.assertEqual(reminder_time, self.now)
        with patch("notifications.scheduler.timezone.now", return_value=self.now):
            dispatch_upcoming_appointment_reminders()
        mock_send.assert_called_once_with(self.appointment)
        self.appointment.refresh_from_db()
        self.assertTrue(self.appointment.reminder_sent)

        mock_send.reset_mock()
        with patch("notifications.scheduler.timezone.now", return_value=self.now):
            dispatch_upcoming_appointment_reminders()
        mock_send.assert_not_called()
