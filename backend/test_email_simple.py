#!/usr/bin/env python
"""
Simple test script for email integration
Run this from the backend directory: python test_email_simple.py
"""

import os
import django

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'backend.settings')
django.setup()

from django.contrib.auth.models import User
from notifications.models import Notification
from notifications.email_service import EmailService

def test_email_service():
    """Test the EmailService directly"""
    print("=== Testing EmailService directly ===")
    
    # Replace with your email for testing
    test_email = input("Enter your email for testing: ").strip()
    
    if not test_email:
        print("No email provided, skipping direct email test")
        return False
    
    print(f"Sending test email to: {test_email}")
    
    try:
        success = EmailService.send_test_email(
            recipient_email=test_email,
            subject="Test Email from Medical App",
            message="This is a test email to verify that the email configuration is working correctly."
        )
        
        if success:
            print("✅ Direct email test PASSED - Check your inbox!")
            return True
        else:
            print("❌ Direct email test FAILED")
            return False
            
    except Exception as e:
        print(f"❌ Error in direct email test: {e}")
        return False

def test_notification_system():
    """Test the notification system with auto-email"""
    print("\n=== Testing Notification System with Auto-Email ===")
    
    try:
        # Get or create a test user
        user, created = User.objects.get_or_create(
            username='test_email_user',
            defaults={
                'email': input("Enter your email for notification test: ").strip(),
                'first_name': 'Test',
                'last_name': 'User'
            }
        )
        
        if not user.email:
            print("No email provided for user, skipping notification test")
            return False
        
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
        
        if notification.email_sent:
            print(f"✅ Notification system test PASSED - Email sent at {notification.email_sent_at}")
            print("Check your inbox for the notification email!")
            return True
        else:
            print("❌ Notification system test FAILED - Email not sent")
            return False
            
    except Exception as e:
        print(f"❌ Error in notification system test: {e}")
        return False

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
