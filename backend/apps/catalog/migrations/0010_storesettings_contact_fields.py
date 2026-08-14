from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('catalog', '0009_instagrampost_created_at_order'),
    ]

    operations = [
        migrations.AlterField(
            model_name='storesettings',
            name='shipping_cost',
            field=models.PositiveIntegerField(default=150000, verbose_name='هزینه ارسال بسته (تومان)'),
        ),
        migrations.AlterField(
            model_name='storesettings',
            name='free_shipping_threshold',
            field=models.PositiveIntegerField(default=0, verbose_name='حداقل خرید برای ارسال رایگان (تومان)'),
        ),
        migrations.AddField(
            model_name='storesettings',
            name='contact_sms_phone',
            field=models.CharField(blank=True, default='', help_text='مثلاً 09123456789 — از طریق پیامک SMS', max_length=20, verbose_name='شماره تماس/پیامک'),
        ),
        migrations.AddField(
            model_name='storesettings',
            name='contact_telegram',
            field=models.CharField(blank=True, default='', help_text='بدون @ — مثلاً lumia_beauty', max_length=100, verbose_name='شناسه تلگرام'),
        ),
        migrations.AddField(
            model_name='storesettings',
            name='contact_whatsapp',
            field=models.CharField(blank=True, default='', help_text='فرمت بین‌المللی بدون + — مثلاً 989123456789', max_length=20, verbose_name='شماره واتساپ'),
        ),
        migrations.AddField(
            model_name='storesettings',
            name='contact_bale',
            field=models.CharField(blank=True, default='', help_text='مثلاً lumia_beauty', max_length=100, verbose_name='شناسه بله'),
        ),
        migrations.AlterField(
            model_name='storesettings',
            name='contact_sms_phone',
            field=models.CharField(blank=True, help_text='مثلاً 09123456789 — از طریق پیامک SMS', max_length=20, verbose_name='شماره تماس/پیامک'),
        ),
        migrations.AlterField(
            model_name='storesettings',
            name='contact_telegram',
            field=models.CharField(blank=True, help_text='بدون @ — مثلاً lumia_beauty', max_length=100, verbose_name='شناسه تلگرام'),
        ),
        migrations.AlterField(
            model_name='storesettings',
            name='contact_whatsapp',
            field=models.CharField(blank=True, help_text='فرمت بین‌المللی بدون + — مثلاً 989123456789', max_length=20, verbose_name='شماره واتساپ'),
        ),
        migrations.AlterField(
            model_name='storesettings',
            name='contact_bale',
            field=models.CharField(blank=True, help_text='مثلاً lumia_beauty', max_length=100, verbose_name='شناسه بله'),
        ),
    ]
