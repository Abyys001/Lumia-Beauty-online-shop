from django.conf import settings as django_settings
from django.db import migrations, models


def seed_admin_phones(apps, schema_editor):
    from apps.accounts.models import normalize_phone

    AuthSettings = apps.get_model('accounts', 'AuthSettings')
    User = apps.get_model('accounts', 'User')

    phones = sorted({
        normalize_phone(p)
        for p in getattr(django_settings, 'ADMIN_PHONES', [])
        if normalize_phone(p)
    })
    if not phones:
        return

    auth, _ = AuthSettings.objects.get_or_create(pk=1)
    auth.admin_phones = sorted(set(auth.admin_phones or []) | set(phones))
    auth.save(update_fields=['admin_phones'])

    User.objects.filter(phone__in=phones).update(is_staff=True, is_superuser=True)


class Migration(migrations.Migration):

    dependencies = [
        ('accounts', '0008_alter_authauditlog_action'),
    ]

    operations = [
        migrations.AddField(
            model_name='authsettings',
            name='admin_phones',
            field=models.JSONField(
                blank=True,
                default=list,
                help_text='هر شماره در این لیست هنگام ثبت‌نام به‌صورت خودکار ادمین می‌شود.',
                verbose_name='شماره‌های ادمین',
            ),
        ),
        migrations.RunPython(seed_admin_phones, migrations.RunPython.noop),
    ]
