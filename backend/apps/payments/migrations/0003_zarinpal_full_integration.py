import uuid

import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


def sync_merchant_from_store(apps, schema_editor):
    StoreSettings = apps.get_model('catalog', 'StoreSettings')
    ZarinpalSettings = apps.get_model('payments', 'ZarinpalSettings')
    try:
        store = StoreSettings.objects.get(pk=1)
    except StoreSettings.DoesNotExist:
        return
    if store.zarinpal_merchant_id:
        zp, _ = ZarinpalSettings.objects.get_or_create(pk=1)
        zp.merchant_id = store.zarinpal_merchant_id
        zp.save(update_fields=['merchant_id'])


class Migration(migrations.Migration):

    dependencies = [
        ('payments', '0002_alter_payment_status'),
        ('catalog', '0002_storesettings'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='ZarinpalSettings',
            fields=[
                ('id', models.PositiveSmallIntegerField(default=1, editable=False, primary_key=True, serialize=False)),
                ('merchant_id', models.CharField(blank=True, max_length=100, verbose_name='کد مرچنت')),
                ('is_sandbox', models.BooleanField(default=True, verbose_name='حالت Sandbox')),
                ('is_mock', models.BooleanField(default=True, verbose_name='Mock محلی (بدون HTTP)')),
                ('callback_url', models.URLField(blank=True, verbose_name='آدرس Callback')),
                ('currency', models.CharField(choices=[('IRR', 'ریال'), ('IRT', 'تومان')], default='IRR', max_length=3, verbose_name='ارز')),
                ('client_id', models.CharField(blank=True, max_length=100, verbose_name='OAuth Client ID')),
                ('client_secret_encrypted', models.TextField(blank=True, verbose_name='OAuth Client Secret')),
                ('terminal_id', models.CharField(blank=True, max_length=50, verbose_name='Terminal ID')),
                ('access_token_encrypted', models.TextField(blank=True)),
                ('refresh_token_encrypted', models.TextField(blank=True)),
                ('token_expires_at', models.DateTimeField(blank=True, null=True)),
                ('auto_reconcile', models.BooleanField(default=False, verbose_name='تسویه خودکار')),
                ('max_retry_attempts', models.PositiveSmallIntegerField(default=3, verbose_name='حداکثر تلاش مجدد')),
                ('enable_api_logging', models.BooleanField(default=True, verbose_name='لاگ API')),
                ('updated_at', models.DateTimeField(auto_now=True)),
            ],
            options={
                'verbose_name': 'تنظیمات زرین‌پال',
                'verbose_name_plural': 'تنظیمات زرین‌پال',
            },
        ),
        migrations.AddField(
            model_name='payment',
            name='card_pan',
            field=models.CharField(blank=True, max_length=20, verbose_name='شماره کارت'),
        ),
        migrations.AddField(
            model_name='payment',
            name='error_code',
            field=models.IntegerField(blank=True, null=True, verbose_name='کد خطا'),
        ),
        migrations.AddField(
            model_name='payment',
            name='fee',
            field=models.PositiveBigIntegerField(blank=True, null=True, verbose_name='کارمزد'),
        ),
        migrations.AddField(
            model_name='payment',
            name='fee_type',
            field=models.CharField(blank=True, max_length=20, verbose_name='نوع کارمزد'),
        ),
        migrations.AddField(
            model_name='payment',
            name='session_id',
            field=models.CharField(blank=True, max_length=100, verbose_name='Session ID'),
        ),
        migrations.CreateModel(
            name='Refund',
            fields=[
                ('id', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ('amount', models.PositiveBigIntegerField(verbose_name='مبلغ')),
                ('method', models.CharField(choices=[('reverse', 'برگشت فوری (Reverse)'), ('card', 'کارت (GraphQL)'), ('paya', 'پایا (GraphQL)')], max_length=20, verbose_name='روش')),
                ('reason', models.CharField(blank=True, max_length=100, verbose_name='دلیل')),
                ('status', models.CharField(choices=[('pending', 'در انتظار'), ('completed', 'تکمیل شده'), ('failed', 'ناموفق')], default='pending', max_length=20, verbose_name='وضعیت')),
                ('gateway_refund_id', models.CharField(blank=True, max_length=100, verbose_name='شناسه مرجوعی درگاه')),
                ('gateway_response', models.JSONField(blank=True, default=dict)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('initiated_by', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='initiated_refunds', to=settings.AUTH_USER_MODEL)),
                ('payment', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='refunds', to='payments.payment')),
            ],
            options={
                'verbose_name': 'مرجوعی',
                'verbose_name_plural': 'مرجوعی‌ها',
                'ordering': ['-created_at'],
            },
        ),
        migrations.RunPython(sync_merchant_from_store, migrations.RunPython.noop),
    ]
