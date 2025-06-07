import logging
from django.core.mail import send_mail
from django.template.loader import render_to_string
from django.utils.html import strip_tags
from django.conf import settings

logger = logging.getLogger(__name__)

class EmailService:
    """
    Service class for handling email notifications
    """
    
    @staticmethod
    def send_notification_email(notification):
        """
        Send email for a notification object
        
        Args:
            notification: Notification instance with type='email'
            
        Returns:
            bool: True if email was sent successfully, False otherwise
        """
        try:
            # Validate notification
            if notification.type != 'email':
                logger.warning(f"Attempted to send email for non-email notification {notification.id}")
                return False
            
            if not notification.user.email:
                logger.warning(f"User {notification.user.username} has no email address")
                return False
            
            # Prepare email content
            context = {
                'user': notification.user,
                'notification': notification,
                'title': notification.title,
                'message': notification.message,
            }
            
            # Generate HTML content
            html_content = EmailService._generate_html_content(context)
            
            # Generate plain text content (fallback)
            plain_content = strip_tags(html_content)
            
            # Send email
            success = send_mail(
                subject=notification.title,
                message=plain_content,
                from_email=settings.DEFAULT_FROM_EMAIL,
                recipient_list=[notification.user.email],
                html_message=html_content,
                fail_silently=False
            )
            
            if success:
                logger.info(f"Email sent successfully to {notification.user.email} for notification {notification.id}")
                return True
            else:
                logger.error(f"Failed to send email to {notification.user.email} for notification {notification.id}")
                return False
                
        except Exception as e:
            logger.error(f"Error sending email for notification {notification.id}: {str(e)}")
            return False
    
    @staticmethod
    def _generate_html_content(context):
        """
        Generate HTML content for email
        
        Args:
            context: Dictionary with email context data
            
        Returns:
            str: HTML content for email
        """
        user = context['user']
        notification = context['notification']
        
        # Simple HTML template
        html_template = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <meta charset="utf-8">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <title>{notification.title}</title>
            <style>
                body {{
                    font-family: Arial, sans-serif;
                    line-height: 1.6;
                    color: #333;
                    max-width: 600px;
                    margin: 0 auto;
                    padding: 20px;
                }}
                .header {{
                    background-color: #007bff;
                    color: white;
                    padding: 20px;
                    text-align: center;
                    border-radius: 5px 5px 0 0;
                }}
                .content {{
                    background-color: #f8f9fa;
                    padding: 30px;
                    border-radius: 0 0 5px 5px;
                }}
                .message {{
                    background-color: white;
                    padding: 20px;
                    border-radius: 5px;
                    margin: 20px 0;
                    border-left: 4px solid #007bff;
                }}
                .footer {{
                    text-align: center;
                    margin-top: 30px;
                    padding-top: 20px;
                    border-top: 1px solid #dee2e6;
                    color: #6c757d;
                    font-size: 14px;
                }}
                .btn {{
                    display: inline-block;
                    padding: 12px 24px;
                    background-color: #007bff;
                    color: white;
                    text-decoration: none;
                    border-radius: 5px;
                    margin: 10px 0;
                }}
            </style>
        </head>
        <body>
            <div class="header">
                <h1>Medical Appointments System</h1>
            </div>
            
            <div class="content">
                <h2>Hello, {user.first_name or user.username}!</h2>
                
                <div class="message">
                    <h3>{notification.title}</h3>
                    <p>{notification.message}</p>
                </div>
                
                <p>If you have any questions, please contact your healthcare provider or our support team.</p>
                
                <div class="footer">
                    <p>This email was sent automatically by the Medical Appointments System.</p>
                    <p>Please do not reply to this email.</p>
                </div>
            </div>
        </body>
        </html>
        """
        
        return html_template
    
    @staticmethod
    def send_test_email(recipient_email, subject="Test Email", message="This is a test email"):
        """
        Send a test email to verify email configuration
        
        Args:
            recipient_email: Email address to send test to
            subject: Email subject
            message: Email message
            
        Returns:
            bool: True if email was sent successfully, False otherwise
        """
        try:
            # Create a simple object-like structure for consistency with _generate_html_content
            class MockObject:
                def __init__(self, **kwargs):
                    for key, value in kwargs.items():
                        setattr(self, key, value)
            
            context = {
                'user': MockObject(first_name='Test User', username='testuser'),
                'notification': MockObject(title=subject, message=message)
            }
            
            html_content = EmailService._generate_html_content(context)
            plain_content = strip_tags(html_content)
            
            success = send_mail(
                subject=subject,
                message=plain_content,
                from_email=settings.DEFAULT_FROM_EMAIL,
                recipient_list=[recipient_email],
                html_message=html_content,
                fail_silently=False
            )
            
            if success:
                logger.info(f"Test email sent successfully to {recipient_email}")
                return True
            else:
                logger.error(f"Failed to send test email to {recipient_email}")
                return False
                
        except Exception as e:
            logger.error(f"Error sending test email to {recipient_email}: {str(e)}")
            return False
