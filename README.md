# Lumia Beauty — فروشگاه آنلاین آرایشی و بهداشتی

فروشگاه اینترنتی **Lumia Beauty** با معماری Decoupled (Nuxt 3 + Django/DRF)، Docker Compose، پشتیبانی فارسی/RTL، سئو، پرداخت کارت‌به‌کارت با تأیید فروشنده و احراز هویت با موبایل و رمز عبور.

## Tech Stack

| لایه | تکنولوژی |
|------|----------|
| Frontend | Nuxt 3, Tailwind CSS, DaisyUI, Pinia |
| Backend | Django 5, Django REST Framework, WhiteNoise |
| Database | PostgreSQL 16 |
| Cache | Redis 7 |
| Proxy (production) | Liara edge proxy |
| Payment | کارت‌به‌کارت با تأیید دستی فروشنده (زرین‌پال به‌صورت اختیاری وصل است) |

## ساختار پروژه

```
├── backend/               # Django + DRF
├── frontend/              # Nuxt 3
├── docker-compose.yml     # Production / Liara (4 containers)
├── docker-compose.dev.yml # Dev overlay (hot-reload, no Nginx)
└── nginx/                 # Legacy config (not used in Compose)
```

## توسعه محلی (Docker)

```bash
cp .env.example .env

# اولین بار
docker compose -f docker-compose.yml -f docker-compose.dev.yml up -d --build

# روزمره
docker compose -f docker-compose.yml -f docker-compose.dev.yml up -d

docker compose exec backend python manage.py createsuperuser
```

- سایت: http://localhost:3000 (Nuxt dev + devProxy برای `/api`)
- Django admin: http://localhost:8000/django-admin/
- Vue admin: http://localhost:3000/admin/

## Production

دو مسیر دیپلوی پشتیبانی می‌شود:

- **VPS / تک‌سرور (زیر، همین بخش):** یک `docker-compose.yml` با ۴ کانتینر (db, redis, backend, frontend).
- **Liara PaaS (دو اپ جدا + addon های مدیریت‌شده):** ببینید [`deploy.md`](./deploy.md) — این مسیر از `docker-compose.yml` استفاده نمی‌کند؛ هر اپ مستقل از روی Dockerfile خودش ساخته می‌شود و Postgres/Redis addon جدا هستند.

### VPS / تک‌سرور (۴ کانتینر)

Stack: **Postgres + Redis + Django (Gunicorn) + Nuxt SSR** — بدون Nginx داخل Docker. Liara در لایه ورودی مسیریابی می‌کند.

### Sitemap (SEO)

- آدرس: `https://yourdomain.com/sitemap.xml`
- با `@nuxtjs/sitemap` ساخته می‌شود و از API دجانگو (`/api/sitemap-urls/`) محصولات، دسته‌بندی‌ها و مقالات را **در هر درخواست** می‌خواند — با اضافه شدن محصول در پنل ادمین، rebuild لازم نیست.
- در Google Search Console → Sitemaps → آدرس `sitemap.xml` را ثبت کنید.
- `robots.txt` همین آدرس را معرفی می‌کند (`Sitemap: /sitemap.xml`).

### ۱. Build فرانت

`frontend/Dockerfile.prod` یک multi-stage build خودکفاست — `npm install` و `npm run build` را خودش داخل ایمیج اجرا می‌کند. نیازی به build دستی قبل از `docker compose up` نیست؛ کافیست `NUXT_PUBLIC_API_BASE`/`NUXT_PUBLIC_SITE_URL` در `.env` (مرحله‌ی بعد) درست تنظیم شده باشند.

### ۲. تنظیم `.env` برای production

```
APP_ENV=production
DJANGO_DEBUG=False
DJANGO_SECRET_KEY=<کلید-امن-۵۰+کاراکتر>
DJANGO_ALLOWED_HOSTS=yourdomain.com,backend
CSRF_TRUSTED_ORIGINS=https://yourdomain.com
CORS_ALLOWED_ORIGINS=https://yourdomain.com
NUXT_PUBLIC_API_BASE=https://yourdomain.com/api
NUXT_PUBLIC_SITE_URL=https://yourdomain.com
ZARINPAL_CALLBACK_URL=https://yourdomain.com/api/payments/zarinpal/verify/
GUNICORN_WORKERS=2
ADMIN_BYPASS_PHONE=
```

### ۳. Deploy

```bash
docker compose up -d --build
docker compose exec backend python manage.py createsuperuser
```

### مسیریابی Liara (الزامی)

| Path | سرویس |
|------|--------|
| `/api/` | backend:8000 |
| `/django-admin/` | backend:8000 |
| `/static/` | backend:8000 (WhiteNoise) |
| `/media/` | backend:8000 |
| `/` | frontend:3000 |
| `/sitemap.xml` | frontend:3000 |

### تخمین RAM

| سرویس | سقف |
|--------|------|
| Postgres | 400 MB |
| Redis | 150 MB |
| Backend (2 worker) | ~300–400 MB |
| Frontend (.output only) | ~200–300 MB |
| **جمع** | ~1–1.2 GB |

## API Endpoints

| مسیر | توضیح |
|------|-------|
| `GET /api/products/` | لیست محصولات |
| `GET /api/products/{slug}/` | جزئیات محصول |
| `GET /api/products/search/?q=` | جستجوی آنی |
| `POST /api/auth/register/` | ثبت‌نام با موبایل و رمز عبور |
| `POST /api/auth/login/` | ورود و دریافت توکن |
| `GET/POST /api/cart/` | سبد خرید |
| `POST /api/orders/` | ثبت سفارش و دریافت کد خرید ۶ رقمی |
| `GET /api/store/contact/` | راه‌های ارتباطی فروشنده (پیامک، تلگرام، واتس‌اپ، بله) |
| `GET /api/admin/orders/lookup/?code=` | جستجوی سفارش با کد خرید (فقط ادمین) |
| `POST /api/admin/orders/{id}/mark-paid/` | تأیید پرداخت کارت‌به‌کارت (فقط ادمین) |
| `POST /api/payments/zarinpal/request/` | درخواست پرداخت |
| `POST /api/coupons/validate/` | اعتبارسنجی کد تخفیف |
| `GET /api/blog/posts/` | مقالات |

## امنیت Production

- `DEBUG=False`
- Secret ها فقط در `.env`
- PostgreSQL و Redis فقط در شبکه داخلی Docker
- Rate limiting روی API (DRF throttling)
- تأیید پرداخت فقط توسط ادمین (`IsStaff`) و لغو خودکار سفارش‌های پرداخت‌نشده پس از ۷ روز

## لایسنس

MIT
