from django.test import TestCase
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

