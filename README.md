# Lumia Beauty — فروشگاه آنلاین آرایشی و بهداشتی

فروشگاه اینترنتی **Lumia Beauty** با معماری Decoupled (Nuxt 3 + Django/DRF)، Docker Compose، پشتیبانی فارسی/RTL، سئو، پرداخت زرین‌پال و احراز هویت پیامکی کاوه‌نگار.

## Tech Stack

| لایه | تکنولوژی |
|------|----------|
| Frontend | Nuxt 3, Tailwind CSS, DaisyUI, Pinia |
| Backend | Django 5, Django REST Framework |
| Database | PostgreSQL 16 |
| Cache | Redis 7 |
| Proxy | Nginx |
| Payment | زرین‌پال |
| SMS | کاوه‌نگار |

## ساختار پروژه

```
├── backend/          # Django + DRF
├── frontend/         # Nuxt 3
├── nginx/            # کانفیگ Nginx
├── docker-compose.yml
└── docker-compose.prod.yml
```

## راه‌اندازی توسعه

```bash
# 1. کپی متغیرهای محیطی
cp .env.example .env

# 2. اجرای سرویس‌ها
docker compose up --build -d

# 3. ایجاد سوپرادمین
docker compose exec backend python manage.py createsuperuser
```

سایت: http://localhost  
پنل ادمین: http://localhost/admin/

## راه‌اندازی Production (سرور ایران)

### پیش‌نیازها
- Ubuntu 22.04+
- Docker و Docker Compose
- دامنه `.ir` (مثلاً `lumiabeauty.ir`)

### مراحل دپلوی

```bash
# 1. کلون پروژه
git clone https://github.com/Abyys001/Lumia-Beauty-online-shop.git
cd Lumia-Beauty-online-shop

# 2. تنظیم .env برای production
cp .env.example .env
# DJANGO_DEBUG=False
# DJANGO_SECRET_KEY=<کلید-امن-تصادفی>
# ZARINPAL_SANDBOX=False
# ZARINPAL_MERCHANT_ID=<مرچنت-کد>
# KAVENEGAR_API_KEY=<کلید-API>

# 3. اجرا
docker compose -f docker-compose.yml -f docker-compose.prod.yml up -d --build

# 4. Migration و superuser
docker compose exec backend python manage.py migrate
docker compose exec backend python manage.py createsuperuser
```

### SSL با Certbot

```bash
sudo apt install certbot
sudo certbot certonly --standalone -d lumiabeauty.ir -d www.lumiabeauty.ir
# کپی گواهی‌ها به nginx/ssl/
```

### CDN ابر آروان

1. دامنه را در پنل ابر آروان ثبت کنید
2. Origin را به IP سرور تنظیم کنید
3. کش استاتیک (`/static/`, `/media/`, `/_nuxt/`) را فعال کنید
4. Gzip/Brotli را روشن کنید
5. DNS دامنه `.ir` را به CDN ابر آروان اشاره دهید

## API Endpoints

| مسیر | توضیح |
|------|-------|
| `GET /api/products/` | لیست محصولات |
| `GET /api/products/{slug}/` | جزئیات محصول |
| `GET /api/products/search/?q=` | جستجوی آنی |
| `POST /api/auth/otp/request/` | درخواست OTP |
| `POST /api/auth/otp/verify/` | تأیید OTP |
| `GET/POST /api/cart/` | سبد خرید |
| `POST /api/orders/` | ثبت سفارش |
| `POST /api/payments/zarinpal/request/` | درخواست پرداخت |
| `POST /api/coupons/validate/` | اعتبارسنجی کد تخفیف |
| `GET /api/blog/posts/` | مقالات |

## صفحات فرانت‌اند

- `/` — صفحه اصلی
- `/shop` — فروشگاه با فیلتر
- `/shop/[slug]` — جزئیات محصول
- `/cart` — سبد خرید
- `/checkout` — تسویه حساب
- `/blog` — وبلاگ
- `/account` — پنل کاربر
- `/auth` — ورود با OTP

## امنیت Production

- `DEBUG=False`
- Secret ها فقط در `.env`
- PostgreSQL و Redis فقط در شبکه داخلی Docker
- Rate limiting روی OTP
- تأیید دو مرحله‌ای پرداخت زرین‌پال

## لایسنس

MIT
