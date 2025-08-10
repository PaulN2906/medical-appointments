from rest_framework import viewsets, permissions, status
from rest_framework.response import Response
from rest_framework.decorators import action
from django.utils import timezone

from .models import Notification
from .serializers import NotificationSerializer
from .email_service import EmailService

class NotificationViewSet(viewsets.ModelViewSet):
    serializer_class = NotificationSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return Notification.objects.filter(user=self.request.user).order_by('-created_at')

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)
    
    @action(detail=True, methods=['post'])
    def mark_as_read(self, request, pk=None):
        notification = self.get_object()
        notification.read = True
        notification.save()
        return Response({'status': 'marked as read'})

    @action(detail=False, methods=['post'])
    def mark_all_as_read(self, request):
        Notification.objects.filter(user=request.user, read=False).update(read=True)
        return Response({'status': 'all marked as read'})
    
    @action(detail=True, methods=['post'])
    def send_email(self, request, pk=None):
        notification = self.get_object()
        
        if notification.type != 'email':
            return Response(
                {'error': 'This notification is not an email type'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        success = EmailService.send_notification_email(notification)
        if success:
            notification.email_sent = True
            notification.email_sent_at = timezone.now()
            notification.save(update_fields=['email_sent', 'email_sent_at'])
            return Response({'status': 'email sent'})
        return Response(
            {'error': 'Failed to send email'},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )
