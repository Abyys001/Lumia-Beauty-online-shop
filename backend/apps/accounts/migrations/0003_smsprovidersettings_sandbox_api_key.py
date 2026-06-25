from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('accounts', '0002_authsettings_otpsettings_otptemplate_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='smsprovidersettings',
            name='sandbox_api_key_encrypted',
            field=models.TextField(blank=True, verbose_name='کلید Sandbox رمزنگاری‌شده'),
        ),
        migrations.AlterField(
            model_name='smsprovidersettings',
            name='api_key_encrypted',
            field=models.TextField(blank=True, verbose_name='کلید Production رمزنگاری‌شده'),
        ),
        migrations.AlterField(
            model_name='smsprovidersettings',
            name='is_sandbox',
            field=models.BooleanField(default=False, verbose_name='حالت Sandbox'),
        ),
    ]
