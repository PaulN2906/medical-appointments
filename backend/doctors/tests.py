from django.test import TestCase
from django.contrib.auth.models import User
from datetime import date, time, timedelta
from django.db.utils import IntegrityError
from django.urls import reverse
from rest_framework.test import APIClient
from .models import Doctor, Schedule


def next_weekday(d: date) -> date:
    """Return the next weekday (Monday-Friday) on or after ``d``."""
    while d.weekday() >= 5:  # 5 = Saturday, 6 = Sunday
        d += timedelta(days=1)
    return d


class ScheduleModelTest(TestCase):
    def setUp(self):
        user = User.objects.create_user(username='doc', password='pass')
        self.doctor = Doctor.objects.create(user=user, speciality='gen')

    def test_schedule_unique_constraint(self):
        day = next_weekday(date.today() + timedelta(days=1))
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

        schedule_day = next_weekday(date.today() + timedelta(days=1))
        Schedule.objects.create(
            doctor=self.doctor1,
            date=schedule_day,
            start_time=time(9, 0),
            end_time=time(10, 0),
        )
        Schedule.objects.create(
            doctor=self.doctor2,
            date=schedule_day,
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


class ScheduleViewsetCreateTest(TestCase):
    def setUp(self):
        self.client = APIClient()

        user1 = User.objects.create_user(username='d1c', password='pass')
        user2 = User.objects.create_user(username='d2c', password='pass')

        self.doctor1 = Doctor.objects.create(user=user1, speciality='gen')
        self.doctor2 = Doctor.objects.create(user=user2, speciality='gen')

        self.url = reverse('schedule-list')

    def test_doctor_cannot_create_schedule_for_another(self):
        self.client.force_authenticate(user=self.doctor1.user)
        data = {
            'doctor': self.doctor2.id,
            'date': next_weekday(date.today() + timedelta(days=1)),
            'start_time': time(9, 0),
            'end_time': time(10, 0),
            'is_available': True,
        }

        response = self.client.post(self.url, data, format='json')
        self.assertEqual(response.status_code, 201)
        self.assertEqual(response.data['doctor'], self.doctor1.id)

        schedule = Schedule.objects.get(id=response.data['id'])
        self.assertEqual(schedule.doctor, self.doctor1)

    def test_non_doctor_cannot_create_schedule(self):
        user = User.objects.create_user(username='plain', password='pass')
        self.client.force_authenticate(user=user)
        data = {
            'doctor': self.doctor1.id,
            'date': next_weekday(date.today() + timedelta(days=1)),
            'start_time': time(9, 0),
            'end_time': time(10, 0),
            'is_available': True,
        }

        response = self.client.post(self.url, data, format='json')
        self.assertEqual(response.status_code, 403)

