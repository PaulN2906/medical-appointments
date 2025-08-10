import logging
from datetime import datetime, timedelta

from django.utils import timezone

from appointments.models import Appointment
from authentication.models import NotificationPreferences
from .models import Notification

logger = logging.getLogger(__name__)


def dispatch_upcoming_appointment_reminders():
    """Send reminder emails for appointments based on user preferences.

    This function can be executed periodically (e.g. via ``cron`` or
    ``django-crontab``) to deliver reminders without requiring Celery.
    For each confirmed appointment the user's :class:`NotificationPreferences`
    are checked and, if appropriate, an email reminder is sent.
    """
    now = timezone.now()
    appointments = (
        Appointment.objects.filter(status="confirmed")
        .select_related("patient__user", "doctor__user", "schedule")
    )

    for appointment in appointments:
        user = appointment.patient.user

        try:
            prefs = NotificationPreferences.objects.get(user=user)
        except NotificationPreferences.DoesNotExist:
            continue

        if not prefs.appointment_reminders:
            continue

        schedule_dt = datetime.combine(
            appointment.schedule.date, appointment.schedule.start_time
        )
        schedule_dt = timezone.make_aware(schedule_dt, timezone.get_current_timezone())
        reminder_time = schedule_dt - timedelta(hours=prefs.reminder_hours_before)

        # Send the reminder if we are within the target minute
        if reminder_time <= now < reminder_time + timedelta(minutes=1):
            Notification.send_appointment_reminder(appointment)
            logger.info(
                "Dispatched reminder for appointment %s to %s",
                appointment.id,
                user.email,
            )

