#!/bin/sh
set -e

python manage.py migrate

sync_admin_bypass() {
  python manage.py shell -c "
import os
from apps.accounts.models import AuthSettings, User, normalize_phone

phone = normalize_phone(os.environ.get('ADMIN_BYPASS_PHONE', '09916122680'))
if phone:
    AuthSettings.objects.update_or_create(pk=1, defaults={'admin_bypass_phone': phone})
    user, _ = User.objects.get_or_create(phone=phone)
    if not user.is_staff or not user.is_superuser:
        user.is_staff = True
        user.is_superuser = True
        user.save(update_fields=['is_staff', 'is_superuser'])
" 2>/dev/null || true
}

sync_admin_bypass

sync_sms_settings() {
  python manage.py shell -c "
from apps.accounts.services.sms_sync import sync_sms_settings
sync_sms_settings()
" 2>/dev/null || true
}

sync_sms_settings

if [ "$APP_ENV" = "production" ]; then
  python manage.py collectstatic --noinput
  exec gunicorn config.wsgi:application \
    --bind 0.0.0.0:8000 \
    --workers "${GUNICORN_WORKERS:-2}" \
    --max-requests "${GUNICORN_MAX_REQUESTS:-1000}" \
    --max-requests-jitter 50 \
    --timeout 120
fi

# Seed when DB is empty OR when product images are missing from the media volume
# (common after volume reset while Postgres data persists).
python manage.py shell -c "
from apps.catalog.models import Product, ProductImage
from django.conf import settings
import os
import sys

if not Product.objects.exists():
    sys.exit(1)

img = ProductImage.objects.order_by('id').first()
if not img or not img.image:
    sys.exit(1)

path = os.path.join(settings.MEDIA_ROOT, str(img.image))
sys.exit(0 if os.path.isfile(path) else 1)
" 2>/dev/null || python seed_db.py

# Drop stale product caches (may contain old absolute image URLs).
python manage.py shell -c "
from django.core.cache import cache
cache.delete('products_featured')
try:
    cache.delete_pattern('products_list:*')
    cache.delete_pattern('product_detail*')
    cache.delete_pattern('search:*')
except Exception:
    pass
" 2>/dev/null || true

exec python manage.py runserver 0.0.0.0:8000
