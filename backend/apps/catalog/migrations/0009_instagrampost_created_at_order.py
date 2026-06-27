import django.utils.timezone
from django.db import migrations, models


def _column_exists(schema_editor, table, column):
    connection = schema_editor.connection
    with connection.cursor() as cursor:
        if connection.vendor == 'postgresql':
            cursor.execute(
                'SELECT 1 FROM information_schema.columns WHERE table_name=%s AND column_name=%s',
                [table, column],
            )
            return cursor.fetchone() is not None
        description = connection.introspection.get_table_description(cursor, table)
        return any(col.name == column for col in description)


def add_instagrampost_created_at_if_missing(apps, schema_editor):
    InstagramPost = apps.get_model('catalog', 'InstagramPost')
    table = InstagramPost._meta.db_table
    if _column_exists(schema_editor, table, 'created_at'):
        return
    field = models.DateTimeField(auto_now_add=True, default=django.utils.timezone.now)
    field.set_attributes_from_name('created_at')
    schema_editor.add_field(InstagramPost, field)


class Migration(migrations.Migration):

    dependencies = [
        ('catalog', '0008_auto_order_by_created_at'),
    ]

    operations = [
        migrations.RunPython(add_instagrampost_created_at_if_missing, migrations.RunPython.noop),
        migrations.SeparateDatabaseAndState(
            state_operations=[
                migrations.AddField(
                    model_name='instagrampost',
                    name='created_at',
                    field=models.DateTimeField(auto_now_add=True, default=django.utils.timezone.now),
                    preserve_default=False,
                ),
            ],
            database_operations=[],
        ),
        migrations.AlterModelOptions(
            name='instagrampost',
            options={
                'ordering': ['created_at'],
                'verbose_name': 'پست اینستاگرام',
                'verbose_name_plural': 'پست‌های اینستاگرام',
            },
        ),
    ]
