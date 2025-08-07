from rest_framework.test import APITestCase
from django.urls import reverse
from django.contrib.auth.models import User
from patients.models import Patient
from doctors.models import Doctor
from rest_framework.authtoken.models import Token
from .models import UserProfile
from django.contrib.auth.hashers import make_password


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


class BackupCodeAuthTest(APITestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username='backup',
            password='pass1234',
            email='backup@example.com',
        )
        # Create user profile with one hashed backup code
        self.profile = UserProfile.objects.create(
            user=self.user,
            two_fa_enabled=True,
            backup_codes=[make_password('backcode')],
        )

    def test_login_with_backup_code(self):
        url = reverse('user-verify-backup-code')
        response = self.client.post(
            url, {'user_id': self.user.id, 'code': 'backcode'}, format='json'
        )

        self.assertEqual(response.status_code, 200)
        self.assertIn('auth_token', response.cookies)

        # Token should exist and backup code should be consumed
        token_key = response.cookies['auth_token'].value
        self.assertTrue(Token.objects.filter(key=token_key, user=self.user).exists())
        self.profile.refresh_from_db()
        self.assertEqual(self.profile.backup_codes, [])
