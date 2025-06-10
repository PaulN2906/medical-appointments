from django.test import TestCase
from django.contrib.auth.models import User
from datetime import date, time, timedelta
from django.db.utils import IntegrityError
from django.urls import reverse
from rest_framework.test import APIClient
from .models import Doctor, Schedule


class ScheduleModelTest(TestCase):
    def setUp(self):
        user = User.objects.create_user(username='doc', password='pass')
        self.doctor = Doctor.objects.create(user=user, speciality='gen')

    def test_schedule_unique_constraint(self):
        day = date.today() + timedelta(days=1)
        Schedule.objects.create(
            doctor=self.doctor,
            date=day,
            start_time=time(9, 0),
            end_time=time(10, 0),
        )

        with self.assertRaises(IntegrityError):
            Schedule.objects.create(
                doctor=self.doctor,
                date=day,
                start_time=time(9, 0),
                end_time=time(10, 0),
            )


class ScheduleViewsetQuerysetTest(TestCase):
    def setUp(self):
        self.client = APIClient()

        user1 = User.objects.create_user(username='d1', password='pass')
        user2 = User.objects.create_user(username='d2', password='pass')

        self.doctor1 = Doctor.objects.create(user=user1, speciality='gen')
        self.doctor2 = Doctor.objects.create(user=user2, speciality='gen')

        Schedule.objects.create(
            doctor=self.doctor1,
            date=date.today() + timedelta(days=1),
            start_time=time(9, 0),
            end_time=time(10, 0),
        )
        Schedule.objects.create(
            doctor=self.doctor2,
            date=date.today() + timedelta(days=1),
            start_time=time(11, 0),
            end_time=time(12, 0),
        )

    def test_doctor_sees_only_their_schedules(self):
        self.client.force_authenticate(user=self.doctor1.user)
        url = reverse('schedule-list')
        response = self.client.get(url)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]['doctor'], self.doctor1.id)

    def test_staff_sees_all_schedules(self):
        staff = User.objects.create_user(username='staff', password='pass', is_staff=True)
        self.client.force_authenticate(user=staff)
        url = reverse('schedule-list')
        response = self.client.get(url)
        self.assertEqual(len(response.data), 2)

