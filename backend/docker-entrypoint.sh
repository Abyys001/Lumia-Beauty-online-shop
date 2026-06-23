#!/bin/sh
set -e

python manage.py migrate

if [ "$APP_ENV" = "production" ]; then
  python manage.py collectstatic --noinput
  exec gunicorn config.wsgi:application \
    --bind 0.0.0.0:8000 \
    --workers "${GUNICORN_WORKERS:-4}" \
    --timeout 120
fi

python manage.py shell -c "
from apps.catalog.models import Product
import sys
sys.exit(0 if Product.objects.exists() else 1)
" 2>/dev/null || python seed_db.py

exec python manage.py runserver 0.0.0.0:8000
