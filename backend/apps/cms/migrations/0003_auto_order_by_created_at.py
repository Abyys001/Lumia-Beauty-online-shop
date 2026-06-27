import django.utils.timezone
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('cms', '0002_instagrampage'),
    ]

    operations = [
        migrations.AddField(
            model_name='trustbadge',
            name='created_at',
            field=models.DateTimeField(auto_now_add=True, default=django.utils.timezone.now),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='instagrampage',
            name='created_at',
            field=models.DateTimeField(auto_now_add=True, default=django.utils.timezone.now),
            preserve_default=False,
        ),
        migrations.AlterModelOptions(
            name='trustbadge',
            options={'ordering': ['created_at'], 'verbose_name': 'نشان اعتماد', 'verbose_name_plural': 'نشان\u200cهای اعتماد'},
        ),
        migrations.AlterModelOptions(
            name='instagrampage',
            options={'ordering': ['created_at'], 'verbose_name': 'پیج اینستاگرام', 'verbose_name_plural': 'پیج\u200cهای اینستاگرام'},
        ),
    ]
