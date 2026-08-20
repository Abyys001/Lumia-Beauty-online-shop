from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('accounts', '0006_sms_provider_profiles'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='authsettings',
            name='otp_login_enabled',
        ),
        migrations.DeleteModel(
            name='SmsLog',
        ),
        migrations.DeleteModel(
            name='OtpRequest',
        ),
        migrations.DeleteModel(
            name='OtpSettings',
        ),
        migrations.DeleteModel(
            name='OtpTemplate',
        ),
        migrations.DeleteModel(
            name='SmsProviderProfile',
        ),
        migrations.DeleteModel(
            name='SmsProviderSettings',
        ),
    ]
