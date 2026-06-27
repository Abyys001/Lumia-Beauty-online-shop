from django.db import migrations, models


def seed_profiles_from_singleton(apps, schema_editor):
    SmsProviderSettings = apps.get_model('accounts', 'SmsProviderSettings')
    SmsProviderProfile = apps.get_model('accounts', 'SmsProviderProfile')
    OtpTemplate = apps.get_model('accounts', 'OtpTemplate')

    defaults = {
        'mock': {'base_url': ''},
        'smsir': {'base_url': 'https://api.sms.ir/v1'},
        'iranpayamak': {'base_url': 'https://api.iranpayamak.com'},
    }
    for provider_type, extra in defaults.items():
        SmsProviderProfile.objects.get_or_create(
            provider_type=provider_type,
            defaults=extra,
        )

    try:
        singleton = SmsProviderSettings.objects.get(pk=1)
    except SmsProviderSettings.DoesNotExist:
        singleton = None

    if singleton:
        active_type = singleton.provider_mode or 'mock'
        shared_fields = [
            'api_key_encrypted', 'sandbox_api_key_encrypted', 'base_url', 'is_sandbox',
            'last_test_at', 'last_test_status', 'last_test_message',
            'line_number', 'number_format', 'panel_username', 'panel_password_encrypted',
            'bearer_token_encrypted', 'bearer_token_expires_at',
        ]
        for provider_type in ('mock', 'smsir', 'iranpayamak'):
            profile = SmsProviderProfile.objects.get(provider_type=provider_type)
            if provider_type == active_type:
                for field in shared_fields:
                    setattr(profile, field, getattr(singleton, field, '' if field.endswith('_encrypted') else None))
                if not profile.base_url:
                    profile.base_url = defaults[provider_type]['base_url']
                profile.is_active = bool(singleton.is_active)
                profile.save()
            elif provider_type == 'smsir' and active_type != 'smsir':
                if singleton.sandbox_api_key_encrypted and not profile.sandbox_api_key_encrypted:
                    profile.sandbox_api_key_encrypted = singleton.sandbox_api_key_encrypted
                    profile.save(update_fields=['sandbox_api_key_encrypted', 'updated_at'])

        if not SmsProviderProfile.objects.filter(is_active=True).exists():
            mock = SmsProviderProfile.objects.get(provider_type='mock')
            mock.is_active = True
            mock.save(update_fields=['is_active', 'updated_at'])

        if active_type == 'iranpayamak':
            OtpTemplate.objects.filter(provider_type='').update(provider_type='iranpayamak')
        elif active_type == 'smsir':
            OtpTemplate.objects.filter(provider_type='').update(provider_type='smsir')


class Migration(migrations.Migration):

    dependencies = [
        ('accounts', '0005_iranpayamak_provider'),
    ]

    operations = [
        migrations.CreateModel(
            name='SmsProviderProfile',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('provider_type', models.CharField(
                    choices=[('mock', 'Mock (توسعه)'), ('smsir', 'SMS.ir'), ('iranpayamak', 'IranPayamak')],
                    max_length=20, unique=True, verbose_name='ارائه‌دهنده',
                )),
                ('api_key_encrypted', models.TextField(blank=True, verbose_name='کلید Production رمزنگاری‌شده')),
                ('sandbox_api_key_encrypted', models.TextField(blank=True, verbose_name='کلید Sandbox رمزنگاری‌شده')),
                ('base_url', models.CharField(blank=True, default='', max_length=200, verbose_name='Base URL')),
                ('is_sandbox', models.BooleanField(default=False, verbose_name='حالت Sandbox')),
                ('is_active', models.BooleanField(default=False, verbose_name='فعال')),
                ('last_test_at', models.DateTimeField(blank=True, null=True, verbose_name='آخرین تست')),
                ('last_test_status', models.CharField(
                    choices=[('ok', 'موفق'), ('failed', 'ناموفق'), ('unknown', 'نامشخص')],
                    default='unknown', max_length=20, verbose_name='وضعیت تست',
                )),
                ('last_test_message', models.TextField(blank=True, verbose_name='پیام تست')),
                ('line_number', models.CharField(blank=True, max_length=30, verbose_name='شماره خط IranPayamak')),
                ('number_format', models.CharField(
                    choices=[('english', 'English'), ('persian', 'Persian')],
                    default='english', max_length=10, verbose_name='فرمت اعداد پیامک',
                )),
                ('panel_username', models.CharField(blank=True, max_length=100, verbose_name='نام کاربری پنل')),
                ('panel_password_encrypted', models.TextField(blank=True, verbose_name='رمز پنل رمزنگاری‌شده')),
                ('bearer_token_encrypted', models.TextField(blank=True, verbose_name='توکن Bearer رمزنگاری‌شده')),
                ('bearer_token_expires_at', models.DateTimeField(blank=True, null=True, verbose_name='انقضای Bearer')),
                ('updated_at', models.DateTimeField(auto_now=True)),
            ],
            options={
                'verbose_name': 'پروفایل SMS',
                'verbose_name_plural': 'پروفایل‌های SMS',
                'ordering': ['provider_type'],
            },
        ),
        migrations.AddField(
            model_name='otptemplate',
            name='provider_type',
            field=models.CharField(
                blank=True,
                choices=[('mock', 'Mock (توسعه)'), ('smsir', 'SMS.ir'), ('iranpayamak', 'IranPayamak')],
                default='',
                max_length=20,
                verbose_name='ارائه‌دهنده',
            ),
        ),
        migrations.RunPython(seed_profiles_from_singleton, migrations.RunPython.noop),
    ]
