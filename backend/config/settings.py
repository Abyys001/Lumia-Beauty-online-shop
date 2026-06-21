"""
Django settings for Lumia Beauty project.
"""

import os
from datetime import timedelta
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent

SECRET_KEY = os.environ.get('DJANGO_SECRET_KEY', 'dev-insecure-key-change-me')
DEBUG = os.environ.get('DJANGO_DEBUG', 'True').lower() in ('true', '1', 'yes')

ALLOWED_HOSTS = [
    h.strip() for h in os.environ.get('DJANGO_ALLOWED_HOSTS', 'localhost,127.0.0.1').split(',')
    if h.strip()
]

INSTALLED_APPS = [
    'jazzmin',
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
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
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
    CORS_ALLOWED_ORIGINS = [
        origin.strip()
        for origin in os.environ.get('CSRF_TRUSTED_ORIGINS', 'http://localhost').split(',')
        if origin.strip()
    ]
    CSRF_TRUSTED_ORIGINS = CORS_ALLOWED_ORIGINS

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
        'rest_framework.permissions.AllowAny',
    ),
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
    'REFRESH_TOKEN_LIFETIME': timedelta(days=7),
    'ROTATE_REFRESH_TOKENS': True,
}

ZARINPAL_MERCHANT_ID = os.environ.get('ZARINPAL_MERCHANT_ID', '')
ZARINPAL_SANDBOX = os.environ.get('ZARINPAL_SANDBOX', 'True').lower() in ('true', '1', 'yes')
ZARINPAL_CALLBACK_URL = os.environ.get('ZARINPAL_CALLBACK_URL', 'http://localhost/api/payments/zarinpal/verify/')

KAVENEGAR_API_KEY = os.environ.get('KAVENEGAR_API_KEY', '')
KAVENEGAR_TEMPLATE = os.environ.get('KAVENEGAR_TEMPLATE', 'verify')

FRONTEND_URL = os.environ.get('NUXT_PUBLIC_SITE_URL', 'http://localhost')

OTP_EXPIRY_SECONDS = 120
OTP_RATE_LIMIT = 3
OTP_RATE_WINDOW_SECONDS = 600

if not DEBUG:
    SECURE_SSL_REDIRECT = True
    SESSION_COOKIE_SECURE = True
    CSRF_COOKIE_SECURE = True
    SECURE_BROWSER_XSS_FILTER = True
    SECURE_CONTENT_TYPE_NOSNIFF = True

JAZZMIN_SETTINGS = {
    'site_title': 'Lumia Beauty',
    'site_header': 'Lumia Beauty',
    'site_brand': 'لومیا بیوتی',
    'welcome_sign': 'به پنل مدیریت لومیا بیوتی خوش آمدید',
    'copyright': 'Lumia Beauty',
    'search_model': ['catalog.Product', 'orders.Order'],
    'topmenu_links': [
        {'name': 'مشاهده سایت', 'url': '/', 'new_window': True},
    ],
    'language_chooser': False,
    'show_sidebar': True,
    'navigation_expanded': True,
    'order_with_respect_to': [
        'catalog', 'orders', 'payments', 'accounts', 'coupons', 'blog', 'cart',
    ],
    'icons': {
        'accounts.User': 'fas fa-users',
        'catalog.Product': 'fas fa-spray-can',
        'catalog.Category': 'fas fa-folder',
        'catalog.Brand': 'fas fa-tag',
        'orders.Order': 'fas fa-shopping-bag',
        'payments.Payment': 'fas fa-credit-card',
        'coupons.Coupon': 'fas fa-percent',
        'blog.Post': 'fas fa-newspaper',
    },
    'custom_css': 'admin/css/rtl.css',
}

JAZZMIN_UI_TWEAKS = {
    'theme': 'flatly',
    'dark_mode_theme': None,
    'navbar': 'navbar-white navbar-light',
    'sidebar': 'sidebar-dark-primary',
    'accent': 'accent-rose',
    'brand_colour': 'navbar-light',
}
