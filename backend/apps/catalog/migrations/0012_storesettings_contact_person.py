from django.conf import settings as django_settings
from django.db import migrations, models


def seed_owner_contact(apps, schema_editor):
    """Fill the seller contact details with the store owner, without overwriting edits."""
    StoreSettings = apps.get_model('catalog', 'StoreSettings')

    phone = (getattr(django_settings, 'OWNER_PHONE', '') or '').strip()
    name = (getattr(django_settings, 'OWNER_NAME', '') or '').strip()
    if not phone and not name:
        return

    obj, _ = StoreSettings.objects.get_or_create(pk=1)
    updates = []
    if name and not obj.contact_person_name:
        obj.contact_person_name = name
        updates.append('contact_person_name')
    if phone and not obj.contact_sms_phone:
        obj.contact_sms_phone = phone
        updates.append('contact_sms_phone')
    if phone and not obj.contact_whatsapp:
        obj.contact_whatsapp = f'98{phone.lstrip("0")}'
        updates.append('contact_whatsapp')
    if updates:
        obj.save(update_fields=updates)


class Migration(migrations.Migration):

    dependencies = [
        ('catalog', '0011_alter_category_sort_order_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='storesettings',
            name='contact_person_name',
            field=models.CharField(
                blank=True,
                help_text='نامی که به مشتری نمایش داده می‌شود — مثلاً خانم قراچه',
                max_length=100,
                verbose_name='نام مسئول فروش',
            ),
        ),
        migrations.RunPython(seed_owner_contact, migrations.RunPython.noop),
    ]
