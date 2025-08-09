#!/usr/bin/env python
"""
Simple test script for email integration
Run this from the backend directory: python test_email_simple.py
"""

import os
import django
import pytest

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'backend.settings')
django.setup()

from django.contrib.auth.models import User
from notifications.models import Notification
from notifications.email_service import EmailService

def test_email_service():
    """Test the EmailService directly"""
    print("=== Testing EmailService directly ===")

    # Use TEST_EMAIL env var instead of interactive input
    test_email = os.getenv("TEST_EMAIL")
    if not test_email:
        pytest.skip("TEST_EMAIL not configured")

    print(f"Sending test email to: {test_email}")

    success = EmailService.send_test_email(
        recipient_email=test_email,
        subject="Test Email from Medical App",
        message="This is a test email to verify that the email configuration is working correctly.",
    )

    assert success
    return True

def test_notification_system():
    """Test the notification system with auto-email"""
    print("\n=== Testing Notification System with Auto-Email ===")

    # Get or create a test user
    test_email = os.getenv("TEST_EMAIL")
    if not test_email:
        pytest.skip("TEST_EMAIL not configured")

    user, created = User.objects.get_or_create(
        username='test_email_user',
        defaults={
            'email': test_email,
            'first_name': 'Test',
            'last_name': 'User'
        }
    )

    print(f"Using test user: {user.username} ({user.email})")

    # Create an email notification (this should trigger auto-send)
    notification = Notification.objects.create(
        user=user,
        type='email',
        title='Test Notification Email',
        message='This is a test notification created to verify that emails are sent automatically when notifications are created.'
    )

    print(f"Created notification {notification.id}")

    # Refresh from database to get updated email_sent status
    notification.refresh_from_db()

    assert notification.email_sent
    return True


def main():
    print("🚀 Starting Email Integration Tests")
    print("=" * 50)

    # Test 1: Direct email service
    test1_passed = test_email_service()

    # Test 2: Notification system
    test2_passed = test_notification_system()

    # Summary
    print("\n" + "=" * 50)
    print("📊 TEST SUMMARY:")
    print(f"Direct Email Test: {'✅ PASSED' if test1_passed else '❌ FAILED'}")
    print(f"Notification Email Test: {'✅ PASSED' if test2_passed else '❌ FAILED'}")

    if all([test1_passed, test2_passed]):
        print("\n🎉 ALL TESTS PASSED! Email integration is working correctly!")
    else:
        print("\n⚠️  Some tests failed. Check the error messages above.")
        print("Common issues:")
        print("- Check your .env file EMAIL_* settings")
        print("- Verify Gmail App Password is correct")
        print("- Check internet connection")

if __name__ == "__main__":
    main()
