from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('catalog', '0006_inventory_shells'),
    ]

    operations = [
        migrations.SeparateDatabaseAndState(
            state_operations=[
                migrations.RemoveField(
                    model_name='review',
                    name='image',
                ),
            ],
            database_operations=[
                migrations.RunSQL(
                    sql='ALTER TABLE catalog_review DROP COLUMN IF EXISTS image;',
                    reverse_sql=migrations.RunSQL.noop,
                ),
            ],
        ),
    ]
