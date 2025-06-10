from django.test import TestCase
from django.contrib.auth.models import User
from .models import Patient


class PatientModelTest(TestCase):
    def test_str_representation(self):
        user = User.objects.create_user(
            username='pat', password='pass', first_name='John', last_name='Doe'
        )
        patient = Patient.objects.create(user=user)
        self.assertEqual(str(patient), 'Patient: John Doe')
