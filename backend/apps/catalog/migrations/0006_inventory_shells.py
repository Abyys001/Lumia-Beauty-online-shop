import uuid

import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


def set_default_pack_sizes(apps, schema_editor):
    StoreSettings = apps.get_model('catalog', 'StoreSettings')
    for obj in StoreSettings.objects.all():
        if not obj.default_stock_pack_sizes:
            obj.default_stock_pack_sizes = [1, 6, 12, 24]
            obj.save(update_fields=['default_stock_pack_sizes'])


class Migration(migrations.Migration):

    dependencies = [
        ('catalog', '0005_storesettings_shipping'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.AddField(
            model_name='storesettings',
            name='default_low_stock_threshold',
            field=models.PositiveSmallIntegerField(default=5, verbose_name='آستانه پیش‌فرض موجودی کم'),
        ),
        migrations.AddField(
            model_name='storesettings',
            name='default_stock_pack_sizes',
            field=models.JSONField(blank=True, default=list, verbose_name='اندازه پیش‌فرض بسته\u200cها'),
        ),
        migrations.AddField(
            model_name='product',
            name='low_stock_threshold',
            field=models.PositiveSmallIntegerField(
                blank=True,
                help_text='خالی = استفاده از پیش\u200cفرض فروشگاه',
                null=True,
                verbose_name='آستانه موجودی کم',
            ),
        ),
        migrations.AddField(
            model_name='product',
            name='pack_label',
            field=models.CharField(default='شل', max_length=20, verbose_name='برچسب بسته'),
        ),
        migrations.AddField(
            model_name='product',
            name='stock_pack_sizes',
            field=models.JSONField(
                blank=True,
                default=list,
                help_text='لیست اعداد — مثلاً [1, 6, 12] یعنی هر شل ۱۲ عدد',
                verbose_name='اندازه بسته\u200cها',
            ),
        ),
        migrations.AddField(
            model_name='product',
            name='stock_unit_label',
            field=models.CharField(default='عدد', max_length=20, verbose_name='واحد شمارش'),
        ),
        migrations.CreateModel(
            name='StockMovement',
            fields=[
                ('id', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ('delta', models.IntegerField(verbose_name='تغییر')),
                ('stock_before', models.PositiveIntegerField(verbose_name='موجودی قبل')),
                ('stock_after', models.PositiveIntegerField(verbose_name='موجودی بعد')),
                ('pack_size', models.PositiveIntegerField(blank=True, null=True, verbose_name='اندازه بسته')),
                ('pack_count', models.IntegerField(blank=True, null=True, verbose_name='تعداد بسته')),
                ('reason', models.CharField(
                    choices=[
                        ('manual', 'تعدیل دستی'),
                        ('purchase', 'ورودی خرید'),
                        ('inventory_count', 'انبارگردانی'),
                        ('correction', 'اصلاح'),
                    ],
                    default='manual',
                    max_length=30,
                    verbose_name='دلیل',
                )),
                ('note', models.CharField(blank=True, max_length=300, verbose_name='یادداشت')),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('created_by', models.ForeignKey(
                    blank=True,
                    null=True,
                    on_delete=django.db.models.deletion.SET_NULL,
                    related_name='stock_movements',
                    to=settings.AUTH_USER_MODEL,
                )),
                ('product', models.ForeignKey(
                    on_delete=django.db.models.deletion.CASCADE,
                    related_name='stock_movements',
                    to='catalog.product',
                    verbose_name='محصول',
                )),
            ],
            options={
                'verbose_name': 'حرکت انبار',
                'verbose_name_plural': 'حرکات انبار',
                'ordering': ['-created_at'],
            },
        ),
        migrations.RunPython(set_default_pack_sizes, migrations.RunPython.noop),
    ]
