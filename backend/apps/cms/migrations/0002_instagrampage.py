import uuid

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('cms', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='InstagramPage',
            fields=[
                ('id', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ('username', models.CharField(help_text='بدون @ — مثال: lumia.beauty', max_length=100, verbose_name='آیدی اینستاگرام')),
                ('label', models.CharField(help_text='مثال: فروش ادکلن این پیج', max_length=200, verbose_name='برچسب')),
                ('sort_order', models.PositiveIntegerField(default=0, verbose_name='ترتیب')),
                ('is_active', models.BooleanField(default=True, verbose_name='فعال')),
            ],
            options={
                'verbose_name': 'پیج اینستاگرام',
                'verbose_name_plural': 'پیج‌های اینستاگرام',
                'ordering': ['sort_order', 'username'],
            },
        ),
    ]
