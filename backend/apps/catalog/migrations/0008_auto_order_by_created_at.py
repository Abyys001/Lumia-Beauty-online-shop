import django.utils.timezone
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('catalog', '0007_remove_review_image'),
    ]

    operations = [
        migrations.AddField(
            model_name='productimage',
            name='created_at',
            field=models.DateTimeField(auto_now_add=True, default=django.utils.timezone.now),
            preserve_default=False,
        ),
        migrations.AlterModelOptions(
            name='category',
            options={'ordering': ['created_at'], 'verbose_name': 'دسته\u200cبندی', 'verbose_name_plural': 'دسته\u200cبندی\u200cها'},
        ),
        migrations.AlterModelOptions(
            name='productimage',
            options={'ordering': ['created_at'], 'verbose_name': 'تصویر محصول', 'verbose_name_plural': 'تصاویر محصول'},
        ),
    ]
