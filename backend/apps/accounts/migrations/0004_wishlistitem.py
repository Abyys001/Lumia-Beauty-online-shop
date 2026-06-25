import uuid

import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('catalog', '0001_initial'),
        ('accounts', '0003_smsprovidersettings_sandbox_api_key'),
    ]

    operations = [
        migrations.CreateModel(
            name='WishlistItem',
            fields=[
                ('id', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('product', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='wishlisted_by', to='catalog.product', verbose_name='محصول')),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='wishlist_items', to=settings.AUTH_USER_MODEL, verbose_name='کاربر')),
            ],
            options={
                'verbose_name': 'علاقه‌مندی',
                'verbose_name_plural': 'علاقه‌مندی‌ها',
                'ordering': ['-created_at'],
            },
        ),
        migrations.AddConstraint(
            model_name='wishlistitem',
            constraint=models.UniqueConstraint(fields=('user', 'product'), name='unique_wishlist_per_user_product'),
        ),
    ]
