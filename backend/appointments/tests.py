from django.test import TestCase
from rest_framework.test import APIClient
from django.urls import reverse
from django.utils import timezone
from django.conf import settings
from datetime import time, timedelta
from django.contrib.auth.models import User
from doctors.models import Doctor, Schedule
from patients.models import Patient
from .models import Appointment
from .serializers import AppointmentSerializer


def _next_weekday():
    date = timezone.localdate() + timedelta(days=1)
    while date.weekday() >= 5:
        date += timedelta(days=1)
    return date


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
            date=_next_weekday(),
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
            date=_next_weekday(),
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

        response = client.post(url, data, format='json', secure=True)
        self.assertEqual(response.status_code, 201)

        self.schedule.refresh_from_db()
        self.assertFalse(self.schedule.is_available)

    def test_patient_cannot_create_appointment_for_another_patient(self):
        other_user = User.objects.create_user(username='other', password='pass')
        Patient.objects.create(user=other_user)

        client = APIClient()
        client.force_authenticate(user=other_user)
        url = reverse('appointment-list')
        data = {
            'patient': self.patient.id,
            'doctor': self.doctor.id,
            'schedule': self.schedule.id,
        }

        response = client.post(url, data, format='json', secure=True)
        self.assertEqual(response.status_code, 403)

    def test_double_booking_prevention(self):
        client = APIClient()
        client.force_authenticate(user=self.patient_user)
        url = reverse('appointment-list')
        data = {
            'patient': self.patient.id,
            'doctor': self.doctor.id,
            'schedule': self.schedule.id,
        }

        first = client.post(url, data, format='json', secure=True)
        self.assertEqual(first.status_code, 201)

        second = client.post(url, data, format='json', secure=True)
        self.assertEqual(second.status_code, 400)
        self.assertEqual(Appointment.objects.count(), 1)

    def test_cancelling_updates_schedule_availability(self):
        client = APIClient()
        client.force_authenticate(user=self.patient_user)
        url = reverse('appointment-list')
        data = {
            'patient': self.patient.id,
            'doctor': self.doctor.id,
            'schedule': self.schedule.id,
        }

        response = client.post(url, data, format='json', secure=True)
        self.assertEqual(response.status_code, 201)
        appointment_id = response.data['id']

        self.schedule.refresh_from_db()
        self.assertFalse(self.schedule.is_available)

        cancel_url = reverse('appointment-cancel', kwargs={'pk': appointment_id})
        cancel_response = client.post(cancel_url, secure=True)
        self.assertEqual(cancel_response.status_code, 200)

        self.schedule.refresh_from_db()
        self.assertTrue(self.schedule.is_available)

    def test_patient_cannot_confirm_appointment(self):
        client = APIClient()
        client.force_authenticate(user=self.patient_user)
        url = reverse('appointment-list')
        data = {
            'patient': self.patient.id,
            'doctor': self.doctor.id,
            'schedule': self.schedule.id,
        }

        response = client.post(url, data, format='json', secure=True)
        self.assertEqual(response.status_code, 201)
        appointment_id = response.data['id']

        confirm_url = reverse('appointment-confirm', kwargs={'pk': appointment_id})
        confirm_response = client.post(confirm_url, secure=True)
        self.assertEqual(confirm_response.status_code, 403)

    def test_schedule_must_match_doctor(self):
        other_user = User.objects.create_user(username='doc3', password='pass')
        other_doctor = Doctor.objects.create(user=other_user, speciality='gen')
        other_schedule = Schedule.objects.create(
            doctor=other_doctor,
            date=_next_weekday(),
            start_time=time(14, 0),
            end_time=time(15, 0),
            is_available=True,
        )

        client = APIClient()
        client.force_authenticate(user=self.patient_user)
        url = reverse('appointment-list')
        data = {
            'patient': self.patient.id,
            'doctor': self.doctor.id,
            'schedule': other_schedule.id,
        }

        response = client.post(url, data, format='json', secure=True)
        self.assertEqual(response.status_code, 400)
        self.assertIn(
            'Selected schedule does not belong to the specified doctor.',
            str(response.data)
        )

