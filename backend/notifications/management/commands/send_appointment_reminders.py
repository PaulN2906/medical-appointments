from django.core.management.base import BaseCommand

from notifications.scheduler import dispatch_upcoming_appointment_reminders


class Command(BaseCommand):
    help = "Send email reminders for upcoming appointments"

    def handle(self, *args, **options):
        dispatch_upcoming_appointment_reminders()
        self.stdout.write(self.style.SUCCESS("Appointment reminders dispatched."))
