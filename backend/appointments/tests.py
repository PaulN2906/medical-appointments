from django.test import TestCase
from rest_framework.test import APIClient
from django.urls import reverse
from django.utils import timezone
from django.conf import settings
from datetime import time, timedelta
from django.contrib.auth.models import User
from doctors.models import Doctor, Schedule
from patients.models import Patient
from .serializers import AppointmentSerializer


class AppointmentTimeZoneTest(TestCase):
    def setUp(self):
        doctor_user = User.objects.create_user(username='doc', password='pass')
        self.doctor = Doctor.objects.create(user=doctor_user, speciality='gen')

        patient_user = User.objects.create_user(username='pat', password='pass')
        self.patient = Patient.objects.create(user=patient_user)

    def test_created_at_uses_project_timezone(self):
        tz = timezone.get_current_timezone()
        self.assertEqual(str(tz), settings.TIME_ZONE)

        schedule = Schedule.objects.create(
            doctor=self.doctor,
            date=timezone.localdate() + timedelta(days=1),
            start_time=time(10, 0),
            end_time=time(11, 0),
            is_available=True,
        )

        serializer = AppointmentSerializer(data={
            'patient': self.patient.id,
            'doctor': self.doctor.id,
            'schedule': schedule.id,
        })

        self.assertTrue(serializer.is_valid(), serializer.errors)
        appointment = serializer.save()

        self.assertEqual(
            timezone.localtime(appointment.created_at).tzinfo,
            tz,
        )


class AppointmentBookingTest(TestCase):
    def setUp(self):
        doctor_user = User.objects.create_user(username='doc2', password='pass')
        self.doctor = Doctor.objects.create(user=doctor_user, speciality='gen')

        patient_user = User.objects.create_user(username='pat2', password='pass')
        self.patient_user = patient_user
        self.patient = Patient.objects.create(user=patient_user)

        self.schedule = Schedule.objects.create(
            doctor=self.doctor,
            date=timezone.localdate() + timedelta(days=1),
            start_time=time(12, 0),
            end_time=time(13, 0),
            is_available=True,
        )

    def test_booking_marks_schedule_unavailable(self):
        client = APIClient()
        client.force_authenticate(user=self.patient_user)
        url = reverse('appointment-list')
        data = {
            'patient': self.patient.id,
            'doctor': self.doctor.id,
            'schedule': self.schedule.id,
        }

        response = client.post(url, data, format='json')
        self.assertEqual(response.status_code, 201)

        self.schedule.refresh_from_db()
        self.assertFalse(self.schedule.is_available)

