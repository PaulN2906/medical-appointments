from django.db import migrations

class Migration(migrations.Migration):
    dependencies = [
        ("authentication", "0004_userprofile_backup_codes"),
    ]

    operations = [
        migrations.RemoveField(
            model_name="notificationpreferences",
            name="marketing_emails",
        ),
    ]
