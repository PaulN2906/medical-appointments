"""
Setup test data pentru race condition test
"""
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'backend.settings')
django.setup()

from django.contrib.auth.models import User
from authentication.models import UserProfile
from doctors.models import Doctor, Schedule
from patients.models import Patient
from appointments.models import Appointment
from datetime import datetime, timedelta

def setup_test_data():
    """Creează datele necesare pentru test"""
    print("🔧 Setting up test data...")
    
    # 1. Creează un doctor de test
    doctor_user, created = User.objects.get_or_create(
        username='test_doctor_race',
        defaults={
            'email': 'doctor_race@test.com',
            'first_name': 'Test',
            'last_name': 'Doctor',
        }
    )
    doctor_user.set_password('TestPassword123!')
    doctor_user.save()
    
    # Creează profile de doctor
    profile, _ = UserProfile.objects.get_or_create(
        user=doctor_user,
        defaults={'role': 'doctor'}
    )
    
    doctor, _ = Doctor.objects.get_or_create(
        user=doctor_user,
        defaults={'speciality': 'General Medicine'}
    )
    
    # 2. Creează un schedule slot pentru test
    tomorrow = datetime.now().date() + timedelta(days=1)
    schedule, created = Schedule.objects.get_or_create(
        doctor=doctor,
        date=tomorrow,
        start_time="10:00:00",
        end_time="11:00:00",
        defaults={'is_available': True}
    )
    
    # Asigură-te că e disponibil și șterge appointment-urile vechi
    Appointment.objects.filter(schedule=schedule).delete()
    schedule.is_available = True
    schedule.save()
    
    # 3. Creează 20 de utilizatori pacienți
    CONCURRENT_REQUESTS = 20
    print(f"📝 Creating {CONCURRENT_REQUESTS} patient users...")
    
    for i in range(CONCURRENT_REQUESTS):
        user, created = User.objects.get_or_create(
            username=f'test_patient_{i}',
            defaults={
                'email': f'patient_{i}@test.com',
                'first_name': f'Patient{i}',
                'last_name': 'Test',
            }
        )
        user.set_password('TestPassword123!')
        user.save()
        
        profile, _ = UserProfile.objects.get_or_create(
            user=user,
            defaults={'role': 'patient'}
        )
        
        patient, _ = Patient.objects.get_or_create(user=user)
    
    print(f"✅ Test data ready:")
    print(f"   Doctor ID: {doctor.id}")
    print(f"   Schedule ID: {schedule.id}")
    print(f"   Schedule Date: {schedule.date} {schedule.start_time}")
    print(f"   Available: {schedule.is_available}")
    
    return doctor.id, schedule.id

if __name__ == "__main__":
    doctor_id, schedule_id = setup_test_data()
    print(f"\n📋 Use these IDs for testing:")
    print(f"   Doctor ID: {doctor_id}")
    print(f"   Schedule ID: {schedule_id}")
