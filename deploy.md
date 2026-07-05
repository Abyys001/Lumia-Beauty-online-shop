# دیپلوی روی Liara PaaS (دو اپ جدا + addon های مدیریت‌شده)

این سند مسیر دیپلوی **متفاوت** از `README.md` (که مدل تک‌سرور/VPS با یک `docker-compose.yml` چهارکانتینری را توضیح می‌دهد) را پوشش می‌دهد:

- **دو اپ جدای Liara**: یکی برای `frontend/`، یکی برای `backend/` — هرکدام از روی همین ریپازیتوری، با Root Directory متفاوت.
- **Postgres و Redis**: به‌صورت addon های مدیریت‌شده‌ی Liara، جدا از دو اپ بالا.

`docker-compose.yml` در این مدل **اجرا نمی‌شود** — Liara هر اپ را مستقل، فقط از روی Dockerfile داخل Root Directory انتخابی، می‌سازد. آن فایل صرفاً برای دولوپمنت لوکال (`docker-compose.dev.yml` overlay) یا آلترناتیو تک‌سرور/VPS معتبر می‌ماند.

## ۱. اپ Backend

| تنظیم | مقدار |
|---|---|
| Root Directory | `backend` |
| Dockerfile | `Dockerfile` (همان `backend/Dockerfile` — بدون ابهام، فقط یک Dockerfile در این پوشه هست) |
| Port | `8000` (entrypoint با `APP_ENV=production` روی این پورت gunicorn را بالا می‌آورد) |

### Environment Variables — Backend

از `docker-compose.yml` (سرویس backend) و `.env.vps` استخراج شده. مقدار هرکدام باید در پنل Liara دستی وارد شود (این‌ها فایل `.env` آپلود نمی‌شوند، تک‌به‌تک در بخش Environment Variables اپ ثبت می‌شوند):

| متغیر | مقدار از کجا می‌آید |
|---|---|
| `APP_ENV` | `production` |
| `USE_SQLITE` | `False` |
| `POSTGRES_DB` | از addon Postgres در Liara |
| `POSTGRES_USER` | از addon Postgres در Liara |
| `POSTGRES_PASSWORD` | از addon Postgres در Liara |
| `POSTGRES_HOST` | از addon Postgres در Liara (هاست داخلی که Liara می‌دهد — نه `db`) |
| `POSTGRES_PORT` | از addon Postgres در Liara (معمولاً `5432`) |
| `DB_CONN_MAX_AGE` | `600` (دلخواه) |
| `REDIS_URL` | ساخته‌شده از addon Redis در Liara، فرمت `redis://[:password@]host:port/0` |
| `DJANGO_SECRET_KEY` | یک مقدار تصادفی طولانی (۵۰+ کاراکتر)، **مشابه `.env.vps` تولید کنید، دوباره استفاده نکنید** |
| `DJANGO_DEBUG` | `False` |
| `DJANGO_ALLOWED_HOSTS` | `yourdomain.com,www.yourdomain.com` + دامنه‌ی داخلی که Liara به اپ backend می‌دهد |
| `CSRF_TRUSTED_ORIGINS` | `https://yourdomain.com,https://www.yourdomain.com` |
| `CORS_ALLOWED_ORIGINS` | `https://yourdomain.com,https://www.yourdomain.com` |
| `DJANGO_SECURE_SSL_REDIRECT` | `True` |
| `DJANGO_SECURE_HSTS_SECONDS` | `0` یا مقدار دلخواه |
| `DJANGO_OTP_DEBUG_CODE` | `False` |
| `GUNICORN_WORKERS` | `2` (بر اساس RAM پلن Liara تنظیم کنید) |
| `GUNICORN_MAX_REQUESTS` | `1000` |
| `ZARINPAL_MERCHANT_ID` | مقدار واقعی زرین‌پال |
| `ZARINPAL_SANDBOX` | `False` |
| `ZARINPAL_MOCK` | `False` |
| `ZARINPAL_CALLBACK_URL` | `https://yourdomain.com/api/payments/zarinpal/verify/` |
| `SMS_PROVIDER` | `smsir` یا `iranpayamak` |
| `SMS_IR_API_KEY` / `IRANPAYAMAK_API_KEY` | بر اساس provider انتخابی |
| `ADMIN_BYPASS_PHONE` | **خالی بماند در production** |

## ۲. اپ Frontend

| تنظیم | مقدار |
|---|---|
| Root Directory | `frontend` |
| Dockerfile | `Dockerfile.prod` — **TODO: تایید کنید Liara مسیر/نام سفارشی Dockerfile را می‌پذیرد** (پوشه‌ی frontend هم `Dockerfile` دولوپمنت و هم `Dockerfile.prod` پروداکشن دارد؛ اگر Liara همیشه دنبال فایلی دقیقاً به نام `Dockerfile` می‌گردد، باید در تنظیمات اپ نام فایل را صراحتاً `Dockerfile.prod` بدهید یا این فایل را در دیپلوی جدا کپی/رینیم کنید) |
| Port | `3000` |

`Dockerfile.prod` فعلی (نسخه‌ی uncommitted) یک multi-stage build خودکفاست — استیج `builder` خودش `npm install && npm run build` را اجرا می‌کند، نیازی به بیلد لوکال قبل از push نیست.

### Environment Variables — Frontend

| متغیر | مقدار |
|---|---|
| `NODE_ENV` | `production` |
| `NUXT_HOST` | `0.0.0.0` |
| `NUXT_PORT` | `3000` |
| `NUXT_PUBLIC_API_BASE` | `https://yourdomain.com/api` (درخواست‌های مرورگر) |
| `NUXT_PUBLIC_SITE_URL` | `https://yourdomain.com` |
| `NUXT_API_INTERNAL_URL` | **TODO** — در `docker-compose.yml` مقدار `http://backend:8000/api` است (هاست‌نیم داخلی Docker Compose) که در مدل دو-اپ-جدا کار نمی‌کند. باید یا آدرس Private Network بین دو اپ Liara (اگر پلن شما این قابلیت را دارد) یا دامنه‌ی عمومی اپ backend (مثل `https://your-backend-app.liara.run/api`) باشد. |

## ۳. مسیریابی دامنه (Path Routing)

`CLAUDE.md`/`README.md` فعلی فرض می‌کنند یک لایه‌ی edge proxy مسیرهای `/api`, `/django-admin`, `/static`, `/media` را به backend و بقیه را به frontend می‌فرستد. در مدل دو-اپ-جدا این باید از طریق تنظیمات **Domain → Path-based routing** پنل Liara روی یک دامنه‌ی سفارشی مشترک بین دو اپ انجام شود.

**TODO:** تایید کنید پلن Liara شما از مسیریابی چندگانه (چند اپ زیر یک دامنه، بر اساس Path) پشتیبانی می‌کند. اگر نه، باید مسیر جایگزین (مثلاً پروکسی کردن `/api` از داخل خود Nuxt/Nitro به backend) در نظر گرفته شود.

## چک‌لیست نهایی قبل از Deploy

- [ ] تایید نام/مسیر سفارشی Dockerfile برای اپ frontend (`Dockerfile.prod`)
- [ ] تایید آدرس داخلی/Private Network بین دو اپ برای `NUXT_API_INTERNAL_URL`
- [ ] تایید پشتیبانی از Path-based routing روی دامنه‌ی مشترک
- [ ] گرفتن مقادیر واقعی addon های Postgres/Redis و map کردن به جدول بالا
- [ ] ست‌کردن `DJANGO_SECRET_KEY` جدید (مقدار `.env.vps` را دوباره استفاده نکنید)
- [ ] `ZARINPAL_MERCHANT_ID` واقعی
