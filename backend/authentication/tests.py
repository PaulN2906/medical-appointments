from rest_framework.test import APITestCase
from django.urls import reverse
from django.contrib.auth.models import User
from patients.models import Patient
from doctors.models import Doctor


class UserRegistrationTest(APITestCase):
    def test_patient_registration_creates_related_models(self):
        url = reverse('user-register')
        data = {
            'username': 'newpatient',
            'password': 'pass1234',
            'email': 'patient@example.com',
            'user_type': 'patient'
        }

        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, 201)

        self.assertTrue(User.objects.filter(username='newpatient').exists())
        self.assertTrue(Patient.objects.filter(user__username='newpatient').exists())

    def test_doctor_registration_creates_related_models(self):
        url = reverse('user-register')
        data = {
            'username': 'docuser',
            'password': 'pass1234',
            'email': 'doc@example.com',
            'user_type': 'doctor'
        }

        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, 201)

        self.assertTrue(User.objects.filter(username='docuser').exists())
        self.assertTrue(Doctor.objects.filter(user__username='docuser').exists())
