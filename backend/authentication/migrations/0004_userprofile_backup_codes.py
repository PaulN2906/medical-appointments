from django.db import migrations, models

class Migration(migrations.Migration):

    dependencies = [
        ('authentication', '0003_notificationpreferences'),
    ]

    operations = [
        migrations.AddField(
            model_name='userprofile',
            name='backup_codes',
            field=models.JSONField(default=list, blank=True),
        ),
    ]
