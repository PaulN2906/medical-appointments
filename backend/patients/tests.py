from django.test import TestCase
from django.contrib.auth.models import User
from django.urls import reverse
from rest_framework.test import APIClient
from doctors.models import Doctor, Schedule
from appointments.models import Appointment
from .models import Patient
from datetime import date, time, timedelta


class PatientModelTest(TestCase):
    def test_str_representation(self):
        user = User.objects.create_user(
            username='pat', password='pass', first_name='John', last_name='Doe'
        )
        patient = Patient.objects.create(user=user)
        self.assertEqual(str(patient), 'Patient: John Doe')


class PatientViewsetQuerysetTest(TestCase):
    def setUp(self):
        self.client = APIClient()

        doctor_user = User.objects.create_user(username='doc', password='pass')
        other_doc_user = User.objects.create_user(username='doc2', password='pass')

        self.doctor = Doctor.objects.create(user=doctor_user, speciality='gen')
        self.other_doctor = Doctor.objects.create(user=other_doc_user, speciality='gen')

        patient1_user = User.objects.create_user(username='p1', password='pass')
        patient2_user = User.objects.create_user(username='p2', password='pass')

        self.patient1 = Patient.objects.create(user=patient1_user)
        self.patient2 = Patient.objects.create(user=patient2_user)

        schedule1 = Schedule.objects.create(
            doctor=self.doctor,
            date=date.today() + timedelta(days=1),
            start_time=time(9, 0),
            end_time=time(10, 0),
        )

        schedule2 = Schedule.objects.create(
            doctor=self.other_doctor,
            date=date.today() + timedelta(days=1),
            start_time=time(11, 0),
            end_time=time(12, 0),
        )

        Appointment.objects.create(patient=self.patient1, doctor=self.doctor, schedule=schedule1)
        Appointment.objects.create(patient=self.patient2, doctor=self.other_doctor, schedule=schedule2)

    def test_doctor_sees_only_his_patients(self):
        self.client.force_authenticate(user=self.doctor.user)
        url = reverse('patient-list')
        response = self.client.get(url)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]['id'], self.patient1.id)

    def test_patient_sees_only_self(self):
        self.client.force_authenticate(user=self.patient1.user)
        url = reverse('patient-list')
        response = self.client.get(url)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]['id'], self.patient1.id)

    def test_staff_sees_all_patients(self):
        staff = User.objects.create_user(username='staff', password='pass', is_staff=True)
        self.client.force_authenticate(user=staff)
        url = reverse('patient-list')
        response = self.client.get(url)
        self.assertEqual(len(response.data), 2)

