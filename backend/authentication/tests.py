from rest_framework.test import APITestCase
from django.urls import reverse
from django.contrib.auth.models import User
from patients.models import Patient
from doctors.models import Doctor
from rest_framework.authtoken.models import Token


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


class ChangePasswordTest(APITestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username='changepass',
            password='oldpassword',
            email='change@example.com',
        )
        self.client.force_authenticate(user=self.user)

    def test_change_password_sets_auth_cookie(self):
        url = reverse('user-change-password')

        response = self.client.post(
            url,
            {
                'current_password': 'oldpassword',
                'new_password': 'Newpass123!',
            },
            format='json',
        )

        self.assertEqual(response.status_code, 200)
        self.assertNotIn('token', response.data)
        self.assertIn('auth_token', response.cookies)

        cookie_token = response.cookies['auth_token'].value
        self.assertTrue(Token.objects.filter(key=cookie_token, user=self.user).exists())
