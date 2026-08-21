#!/bin/sh
set -e

python manage.py migrate

sync_admins() {
  python manage.py shell -c "
from django.conf import settings
from apps.accounts.models import AuthSettings, User, normalize_phone

phones = [normalize_phone(p) for p in settings.ADMIN_PHONES]
phones = [p for p in phones if p]
bypass = normalize_phone(settings.ADMIN_BYPASS_PHONE) if settings.ADMIN_BYPASS_PHONE else ''
owner = normalize_phone(settings.OWNER_PHONE) if settings.OWNER_PHONE else ''
if owner and owner not in phones:
    phones.append(owner)

if phones:
    auth = AuthSettings.get_settings()
    auth.admin_phones = sorted(set(auth.admin_phones or []) | set(phones))
    auth_fields = ['admin_phones']
    if bypass:
        auth.admin_bypass_phone = bypass
        auth_fields.append('admin_bypass_phone')
    auth.save(update_fields=auth_fields)

    for phone in phones:
        user = User.objects.filter(phone=phone).first()
        if user is None:
            # create_user() marks the password unusable, so the owner can still
            # sign up through /api/auth/register/ and pick their own password.
            user = User.objects.create_user(phone=phone)
        fields = []
        if not user.password:
            user.set_unusable_password()
            fields.append('password')
        if not user.is_staff or not user.is_superuser:
            user.is_staff = True
            user.is_superuser = True
            fields += ['is_staff', 'is_superuser']
        if phone == owner and not user.last_name and settings.OWNER_NAME:
            first, _, last = settings.OWNER_NAME.rpartition(' ')
            user.first_name = first
            user.last_name = last
            fields += ['first_name', 'last_name']
        if fields:
            user.save(update_fields=fields)
" 2>/dev/null || true
}

sync_admins

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
