import random
import string

from django.db import migrations, models


def backfill_purchase_codes(apps, schema_editor):
    Order = apps.get_model('orders', 'Order')
    used = set(Order.objects.values_list('purchase_code', flat=True))
    for order in Order.objects.filter(purchase_code='').iterator():
        code = ''.join(random.choices(string.digits, k=6))
        while code in used:
            code = ''.join(random.choices(string.digits, k=6))
        used.add(code)
        order.purchase_code = code
        order.save(update_fields=['purchase_code'])


class Migration(migrations.Migration):

    dependencies = [
        ('orders', '0003_alter_order_shipping_postal_code'),
    ]

    operations = [
        migrations.AddField(
            model_name='order',
            name='shipping_plate_number',
            field=models.CharField(blank=True, max_length=20, verbose_name='شماره پلاک'),
        ),
        migrations.AddField(
            model_name='order',
            name='purchase_code',
            field=models.CharField(default='', max_length=6, verbose_name='کد خرید'),
        ),
        migrations.RunPython(backfill_purchase_codes, migrations.RunPython.noop),
        migrations.AlterField(
            model_name='order',
            name='purchase_code',
            field=models.CharField(max_length=6, unique=True, verbose_name='کد خرید'),
        ),
    ]
