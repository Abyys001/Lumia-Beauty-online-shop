from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('catalog', '0004_remove_storesettings_kavenegar_api_key_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='storesettings',
            name='shipping_cost',
            field=models.PositiveIntegerField(default=50000, verbose_name='هزینه ارسال بسته (تومان)'),
        ),
        migrations.AddField(
            model_name='storesettings',
            name='free_shipping_threshold',
            field=models.PositiveIntegerField(
                default=500000,
                verbose_name='حداقل خرید برای ارسال رایگان (تومان)',
            ),
        ),
    ]
