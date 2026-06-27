# AGENTS.md

This file provides guidance to Codex (Codex.ai/code) when working with code in this repository.

## Commands

### Full stack (Docker)
```bash
cp .env.example .env
docker compose -f docker-compose.yml -f docker-compose.dev.yml up -d --build

# First-time seed
docker compose exec backend python manage.py createsuperuser

# Migrations after model changes
docker compose exec backend python manage.py migrate

# Re-seed demo data
docker compose exec backend python seed_db.py
```

Site (dev): http://localhost:3000 | Admin: http://localhost:3000/admin/

Production (Liara): build frontend locally (`cd frontend && npm run build`), then `docker compose up -d --build` (4 containers, no Nginx).

### Frontend only (no Docker)
```bash
cd frontend
npm install
npm run dev        # dev server on :3000
npm run build      # production build
```

### Backend only (no Docker)
```bash
cd backend
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
python manage.py migrate   # defaults to SQLite
python manage.py runserver
```

No test suite or linter is configured yet.

## Architecture

**Stack:** Nuxt 3 (SSR) → Liara proxy (prod) or direct :3000/:8000 (dev) → Django 5 / DRF | PostgreSQL 16 | Redis 7

Four containers in production (`db`, `redis`, `backend`, `frontend`). Liara routes API/static/media to backend; WhiteNoise serves `/static/`. Dev uses `docker-compose.dev.yml` overlay without Nginx.

### Backend (`backend/`)

Django project at `config/`. Seven Django apps under `apps/`:

| App | Responsibility |
|---|---|
| `accounts` | Custom `User` model (phone-based), OTP via Kavenegar, JWT via simplejwt, address management |
| `catalog` | `Product`, `Category`, `Brand`, `Review`, `InstagramPost`, `StoreSettings` (singleton pk=1) |
| `cart` | Session cart tied to user |
| `orders` | `Order` + `OrderItem`, tracking numbers |
| `payments` | Zarinpal integration (`ZarinpalService`), `Payment`, `PaymentLog` |
| `coupons` | `Coupon` model + usage tracking |
| `blog` | `Post` model |

**Auth flow:** phone → OTP stored in cache (`otp:<phone>`) → verified → JWT pair issued. Rate-limited to `OTP_RATE_LIMIT=3` requests per `OTP_RATE_WINDOW_SECONDS=600`. Tokens: access 15 min, refresh 7 days (rotated).

**Payment flow (Zarinpal):** In `ZARINPAL_SANDBOX=True` mode, `create_payment_request` generates a `MOCK_<order_number>` authority and immediately redirects to the callback URL — no external HTTP call. `verify_payment_callback` detects the `MOCK_` prefix and skips the real verify call. On success: stock decremented, `sales_count` incremented, coupon usage recorded, cart cleared — all in a single `@transaction.atomic`.

**Dev database toggle:** `USE_SQLITE=True` (default when not in Docker) uses SQLite + `LocMemCache`. `USE_SQLITE=False` switches to PostgreSQL + Redis. Docker Compose always sets `USE_SQLITE=False`.

**Admin:** Jazzmin theme with RTL CSS (`static/admin/css/rtl.css`). The app list grouping and index dashboard stats are monkey-patched onto `admin.site` directly in `config/urls.py`. `ProductImage.save()` auto-resizes images to max 1200 px wide via Pillow.

### Frontend (`frontend/`)

Nuxt 3 SSR app. Persian/RTL throughout (`lang="fa"`, `dir="rtl"`). Vazirmatn font loaded from CDN.

**Dual API URL pattern** (in `composables/useApi.ts`): on the server, requests go to `NUXT_API_INTERNAL_URL` (`http://backend:8000/api`); on the client, they go to `NUXT_PUBLIC_API_BASE` (`http://localhost/api`). Always use `apiFetch` from `useApi()` — never call `$fetch` directly — to keep this routing correct across SSR and client.

**State:** Pinia stores live in `stores/`. `plugins/auth.client.ts` calls `auth.loadFromStorage()` on client mount to rehydrate JWT from localStorage.

**Key components:**
- `CartDrawer.vue` — slide-over cart
- `LiveSearch.vue` — debounced `/api/products/search/?q=`
- `FilterSidebar.vue` — category/brand/price filters for shop page

**Sitemap** sources from `/api/__sitemap__/urls` (served by `apps/catalog/sitemap.py`). Pages excluded: `/account`, `/cart`, `/checkout`, `/auth`.

### Environment variables

Key vars (see `.env.example` for full list):

| Variable | Purpose |
|---|---|
| `USE_SQLITE` | `True` = SQLite dev mode (no Postgres/Redis needed) |
| `ZARINPAL_SANDBOX` | `True` = mock payment, no real API calls |
| `KAVENEGAR_API_KEY` | Leave empty in dev; OTP will fail silently |
| `NUXT_API_INTERNAL_URL` | Backend URL for Nuxt SSR (Docker internal) |
| `NUXT_PUBLIC_API_BASE` | Backend URL for browser JS |
