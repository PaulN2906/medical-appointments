from django.test import TestCase
from django.contrib.auth.models import User
from datetime import date, time, timedelta
from django.db.utils import IntegrityError
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
