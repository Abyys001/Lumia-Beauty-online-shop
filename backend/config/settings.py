"""
Django settings for Lumia Beauty project.
"""

import os
from datetime import timedelta
from pathlib import Path

from django.core.exceptions import ImproperlyConfigured

BASE_DIR = Path(__file__).resolve().parent.parent


def env_bool(name, default=False):
    return os.environ.get(name, str(default)).lower() in ('true', '1', 'yes', 'on')


def env_list(name, default=''):
    return [item.strip() for item in os.environ.get(name, default).split(',') if item.strip()]


SECRET_KEY = os.environ.get('DJANGO_SECRET_KEY', 'dev-insecure-key-change-me')
DEBUG = env_bool('DJANGO_DEBUG', True)

if not DEBUG and (
    not SECRET_KEY
    or SECRET_KEY in {'dev-insecure-key-change-me', 'dev-secret-key-change-in-production'}
    or len(set(SECRET_KEY)) < 8
    or len(SECRET_KEY) < 50
):
    raise ImproperlyConfigured('DJANGO_SECRET_KEY must be a strong, unique value when DJANGO_DEBUG=False.')

ALLOWED_HOSTS = env_list('DJANGO_ALLOWED_HOSTS', 'localhost,127.0.0.1')
if not DEBUG and not ALLOWED_HOSTS:
    raise ImproperlyConfigured('DJANGO_ALLOWED_HOSTS must be set when DJANGO_DEBUG=False.')

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'rest_framework',
    'rest_framework_simplejwt',
    'corsheaders',
    'django_filters',
    'apps.accounts',
    'apps.catalog',
    'apps.cart',
    'apps.orders',
    'apps.payments',
    'apps.blog',
    'apps.coupons',
    'apps.admin_api',
    'apps.cms',
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'whitenoise.middleware.WhiteNoiseMiddleware',
    'corsheaders.middleware.CorsMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'config.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [BASE_DIR / 'templates'],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

WSGI_APPLICATION = 'config.wsgi.application'

USE_SQLITE = os.environ.get('USE_SQLITE', 'True').lower() in ('true', '1', 'yes')

if USE_SQLITE:
    DATABASES = {
        'default': {
            'ENGINE': 'django.db.backends.sqlite3',
            'NAME': BASE_DIR / 'db.sqlite3',
        }
    }
else:
    DATABASES = {
        'default': {
            'ENGINE': 'django.db.backends.postgresql',
            'NAME': os.environ.get('POSTGRES_DB', 'lumia_beauty'),
            'USER': os.environ.get('POSTGRES_USER', 'lumia'),
            'PASSWORD': os.environ.get('POSTGRES_PASSWORD', 'lumia_secret'),
            'HOST': os.environ.get('POSTGRES_HOST', 'localhost'),
            'PORT': os.environ.get('POSTGRES_PORT', '5432'),
            'CONN_MAX_AGE': int(os.environ.get('DB_CONN_MAX_AGE', '600')),
            'CONN_HEALTH_CHECKS': True,
        }
    }

AUTH_PASSWORD_VALIDATORS = [
    {'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator'},
    {'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator'},
    {'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator'},
    {'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator'},
]

LANGUAGE_CODE = 'fa-ir'
TIME_ZONE = 'Asia/Tehran'
USE_I18N = True
USE_TZ = True

STATIC_URL = '/static/'
STATIC_ROOT = BASE_DIR / 'staticfiles'
STATICFILES_DIRS = [BASE_DIR / 'static']
MEDIA_URL = '/media/'
MEDIA_ROOT = BASE_DIR / 'media'

if not DEBUG:
    STORAGES = {
        'default': {
            'BACKEND': 'django.core.files.storage.FileSystemStorage',
        },
        'staticfiles': {
            'BACKEND': 'whitenoise.storage.CompressedStaticFilesStorage',
        },
    }

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'
AUTH_USER_MODEL = 'accounts.User'

if DEBUG:
    CORS_ALLOW_ALL_ORIGINS = True
    CSRF_TRUSTED_ORIGINS = [
        'http://localhost:3000', 'http://127.0.0.1:3000',
        'http://localhost:3001', 'http://127.0.0.1:3001',
        'http://localhost:3002', 'http://127.0.0.1:3002',
        'http://localhost:8000', 'http://127.0.0.1:8000',
        'http://localhost:8001', 'http://127.0.0.1:8001',
        'http://localhost:8002', 'http://127.0.0.1:8002',
    ]
else:
    CORS_ALLOWED_ORIGINS = env_list('CORS_ALLOWED_ORIGINS')
    CSRF_TRUSTED_ORIGINS = env_list('CSRF_TRUSTED_ORIGINS')
    if not CORS_ALLOWED_ORIGINS:
        raise ImproperlyConfigured('CORS_ALLOWED_ORIGINS must be set when DJANGO_DEBUG=False.')
    if not CSRF_TRUSTED_ORIGINS:
        raise ImproperlyConfigured('CSRF_TRUSTED_ORIGINS must be set when DJANGO_DEBUG=False.')

CORS_ALLOW_CREDENTIALS = True

REDIS_URL = os.environ.get('REDIS_URL', 'redis://localhost:6379/0')

if USE_SQLITE:
    CACHES = {
        'default': {
            'BACKEND': 'django.core.cache.backends.locmem.LocMemCache',
            'LOCATION': 'lumia-cache',
        }
    }
else:
    CACHES = {
        'default': {
            'BACKEND': 'django_redis.cache.RedisCache',
            'LOCATION': REDIS_URL,
            'OPTIONS': {
                'CLIENT_CLASS': 'django_redis.client.DefaultClient',
            },
            'KEY_PREFIX': 'lumia',
        }
    }

SESSION_ENGINE = 'django.contrib.sessions.backends.cache'
SESSION_CACHE_ALIAS = 'default'

REST_FRAMEWORK = {
    'DEFAULT_AUTHENTICATION_CLASSES': (
        'rest_framework_simplejwt.authentication.JWTAuthentication',
        'rest_framework.authentication.SessionAuthentication',
    ),
    'DEFAULT_PERMISSION_CLASSES': (
        'rest_framework.permissions.IsAuthenticated',
    ),
    'DEFAULT_THROTTLE_CLASSES': (
        'rest_framework.throttling.AnonRateThrottle',
        'rest_framework.throttling.UserRateThrottle',
        'rest_framework.throttling.ScopedRateThrottle',
    ),
    'DEFAULT_THROTTLE_RATES': {
        'anon': os.environ.get('DRF_THROTTLE_ANON', '120/min'),
        'user': os.environ.get('DRF_THROTTLE_USER', '600/min'),
        'payment': os.environ.get('DRF_THROTTLE_PAYMENT', '30/min'),
    },
    'DEFAULT_FILTER_BACKENDS': (
        'django_filters.rest_framework.DjangoFilterBackend',
        'rest_framework.filters.SearchFilter',
        'rest_framework.filters.OrderingFilter',
    ),
    'DEFAULT_PAGINATION_CLASS': 'rest_framework.pagination.PageNumberPagination',
    'PAGE_SIZE': 12,
}

SIMPLE_JWT = {
    'ACCESS_TOKEN_LIFETIME': timedelta(minutes=15),
    # Long-lived + rotated on every refresh: any visit inside the window
    # slides the session forward, so a device effectively stays logged in.
    'REFRESH_TOKEN_LIFETIME': timedelta(days=90),
    'ROTATE_REFRESH_TOKENS': True,
}

ZARINPAL_MERCHANT_ID = os.environ.get('ZARINPAL_MERCHANT_ID', '')
ZARINPAL_SANDBOX = os.environ.get('ZARINPAL_SANDBOX', 'True').lower() in ('true', '1', 'yes')
ZARINPAL_MOCK = os.environ.get('ZARINPAL_MOCK', 'True').lower() in ('true', '1', 'yes')
ZARINPAL_CALLBACK_URL = os.environ.get('ZARINPAL_CALLBACK_URL', 'http://localhost/api/payments/zarinpal/verify/')
ZARINPAL_CLIENT_ID = os.environ.get('ZARINPAL_CLIENT_ID', '')
ZARINPAL_CLIENT_SECRET = os.environ.get('ZARINPAL_CLIENT_SECRET', '')
ZARINPAL_TERMINAL_ID = os.environ.get('ZARINPAL_TERMINAL_ID', '')

# Phones that are promoted to staff/superuser on registration (and on boot).
# The last one is the store owner (خانم قراچه) whose number is shown to customers.
ADMIN_PHONES = [
    p.strip()
    for p in os.environ.get('ADMIN_PHONES', '09916122680,09332279699,09166099383').split(',')
    if p.strip()
]
OWNER_PHONE = os.environ.get('OWNER_PHONE', '09166099383')
OWNER_NAME = os.environ.get('OWNER_NAME', 'خانم قراچه')

ADMIN_BYPASS_PHONE = os.environ.get('ADMIN_BYPASS_PHONE', '')

FRONTEND_URL = os.environ.get('NUXT_PUBLIC_SITE_URL', 'http://localhost')

LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'handlers': {
        'console': {'class': 'logging.StreamHandler'},
    },
}
MAX_CART_ITEM_QUANTITY = int(os.environ.get('MAX_CART_ITEM_QUANTITY', '20'))
# Card-to-card orders that are never confirmed by the seller are cancelled after this many days.
PENDING_ORDER_EXPIRY_DAYS = int(os.environ.get('PENDING_ORDER_EXPIRY_DAYS', '7'))

if not DEBUG:
    SECURE_SSL_REDIRECT = env_bool('DJANGO_SECURE_SSL_REDIRECT', True)
    SESSION_COOKIE_SECURE = True
    CSRF_COOKIE_SECURE = True
    SECURE_CONTENT_TYPE_NOSNIFF = True
    SECURE_PROXY_SSL_HEADER = ('HTTP_X_FORWARDED_PROTO', 'https')
    SECURE_REFERRER_POLICY = 'same-origin'
    X_FRAME_OPTIONS = 'DENY'
    SECURE_HSTS_SECONDS = int(os.environ.get('DJANGO_SECURE_HSTS_SECONDS', '0'))
    SECURE_HSTS_INCLUDE_SUBDOMAINS = env_bool('DJANGO_SECURE_HSTS_INCLUDE_SUBDOMAINS', False)
    SECURE_HSTS_PRELOAD = env_bool('DJANGO_SECURE_HSTS_PRELOAD', False)

