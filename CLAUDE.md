# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Commands

### Full stack (Docker)
```bash
cp .env.example .env
docker compose -f docker-compose.yml -f docker-compose.dev.yml up -d --build

# Daily development (code hot-reloads via volume mounts — no rebuild):
docker compose -f docker-compose.yml -f docker-compose.dev.yml up -d
# Optional: auto-rebuild images when requirements.txt / package.json change:
docker compose -f docker-compose.yml -f docker-compose.dev.yml watch

# First-time seed
docker compose exec backend python manage.py createsuperuser

# Migrations after model changes
docker compose exec backend python manage.py migrate

# Re-seed demo data
docker compose exec backend python seed_db.py

# Tail logs
docker compose logs -f backend
docker compose logs -f frontend
```

**Production (Liara, 4 containers, no Nginx):** `Dockerfile.prod` is a multi-stage build — the PaaS installs deps and runs `npm run build` inside the image, no local build step needed. Set `APP_ENV=production` and `DJANGO_DEBUG=False` in `.env`, then `docker compose up -d --build`. Liara routes `/api`, `/static`, `/media`, `/django-admin` → backend:8000 and `/` → frontend:3000.

Site (dev): http://localhost:3000 | Django admin: http://localhost:8000/django-admin/ | Vue admin: http://localhost:3000/admin

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

**Stack:** Nuxt 3 (SSR) → Liara edge proxy (production) or direct ports (dev) → Django 5 / DRF | PostgreSQL 16 | Redis 7

Four Docker containers in production: `db`, `redis`, `backend`, `frontend`. No Nginx container — Liara proxies `/api`, `/django-admin`, `/static`, `/media` to `backend:8000` and everything else to `frontend:3000`. Static files served by WhiteNoise; media by Django in production.

Local dev uses `docker-compose.dev.yml` overlay: frontend on `:3000` (Nuxt dev + `devProxy` for `/api`), backend on `:8000`.

### Backend (`backend/`)

Django project at `config/`. Eight Django apps under `apps/`:

| App | Responsibility |
|---|---|
| `accounts` | Custom `User` model (phone + password), JWT via simplejwt, auth audit log, address management |
| `catalog` | `Product`, `Category`, `Brand`, `Review`, `InstagramPost`, `StoreSettings` (singleton pk=1) |
| `cart` | Session cart tied to authenticated user |
| `orders` | `Order` + `OrderItem`, tracking numbers |
| `payments` | Zarinpal integration (`ZarinpalService`), `Payment`, `PaymentLog` |
| `coupons` | `Coupon` model + usage tracking |
| `blog` | `Post` model |
| `admin_api` | Staff-only DRF API for the Vue admin dashboard (`/api/admin/*`) |

**Auth flow:** phone + password. Registration requires `first_name` and `last_name` (the name goes on the parcel) plus a client-side password confirmation; login needs only phone + password. `POST /api/auth/register/` and `/api/auth/login/` both return a JWT pair (access 15 min, refresh 7 days, rotated) — lifetimes live on the `AuthSettings` singleton, editable at `/admin/settings` and every attempt is written to `AuthAuditLog`. There is no OTP and no SMS provider: the only phone numbers the app knows about are the seller's contact handles in `StoreSettings.contact_*`. `ADMIN_PHONES` (comma-separated, default `09916122680,09332279699,09166099383`) lists the phones that become staff/superuser automatically — the entrypoint promotes them on boot and `RegisterSerializer` promotes them at sign-up; the list is mirrored onto `AuthSettings.admin_phones` so it survives without the env var. `ADMIN_BYPASS_PHONE` is narrower: that single phone logs in with any password. `OWNER_PHONE` / `OWNER_NAME` (default `09166099383` / خانم قراچه) name the store owner — the migration seeds them into `StoreSettings.contact_person_name` / `contact_sms_phone` / `contact_whatsapp`, which drive the contact page and the checkout payment buttons.

**Checkout flow (card-to-card — the default):** `POST /api/orders/` creates the order with a unique 6-digit `purchase_code` and empties the cart; no gateway is called. The customer sends that code to the seller over SMS / Telegram / WhatsApp / Bale — the handles live on `StoreSettings.contact_*` (public read at `/api/store/contact/`, edited at `/admin/settings/contact`) and drive the buttons on `/checkout/pending`. The seller looks the code up at `/admin/lookup` (`GET /api/admin/orders/lookup/?code=`) and confirms with `POST /api/admin/orders/<id>/mark-paid/`, which runs `confirm_manual_payment`: same fulfilment as a gateway success (stock, `sales_count`, coupon usage, cart) in one `@transaction.atomic`, idempotent, refused for cancelled/refunded orders. After posting the parcel the seller PATCHes `status=shipped` plus a 24-digit `tracking_number` (Persian digits accepted); the customer sees it on `/account/orders/<order_number>`. The Zarinpal path is still wired but nothing in checkout uses it.

**Checkout validation:** `CreateOrderSerializer` declares every shipping field optional and blank-tolerant, then decides in `validate()` what is actually required — nothing when `address_id` is given, otherwise name, phone, province, city, address and postal code, each rejected with its own Persian message keyed by field name. Phone and postal code are folded to ASCII digits (`to_en_digits` in `apps/accounts/models.py`) before being checked against `09XXXXXXXXX` and `\d{10}`. The rules are mirrored client-side in `pages/checkout/index.vue` so the customer is told before a round trip; the server stays the authority. `composables/useFormErrors.ts` spreads any DRF error body — field dict, `detail`, `non_field_errors`, or no body at all — onto per-field slots plus a summary list, and `components/checkout/CheckoutField.vue` renders label, required marker, hint and inline error. Never read only `.detail` from a 400: field errors do not carry it, which is what made every failed checkout say “خطا در ثبت سفارش”.

**Shipping cost:** both numbers live on `StoreSettings` and are edited by the seller at `/admin/settings/shipping` — nothing is hardcoded. `apps/catalog/shipping.py` is the single authority: `shipping_cost` is charged per order, and `free_shipping_threshold` waives it once the basket subtotal reaches it (`0` disables the threshold, which is the original flat-fee behaviour). A coupon of type `free_shipping` waives the fee regardless of the threshold. `pages/checkout/index.vue` mirrors these rules from `GET /api/store/shipping/` so the customer sees «رایگان» and how much more to spend, but the saved order always takes its `shipping_cost` from the server. `apps/catalog/tests_shipping.py` locks the rules.

**Unpaid-order expiry:** pending orders are cancelled `PENDING_ORDER_EXPIRY_DAYS` (default 7) after creation — `apps/orders/services.py`. Nothing is reserved before confirmation, so expiry only flips the status and fails any pending `Payment` row. Run `python manage.py expire_pending_orders [--days N]` from cron; without one, a cache-throttled sweep (once an hour) runs off the order read paths and the admin notifications poll. `OrderSerializer.expires_at` gives the customer the deadline while the order is pending.

**Images & media (why they break, and why they can't now):** Django owns `/media` (uploads) and `/static`, but the browser only ever talks to the frontend origin — every API payload is normalized to a root-relative `/media/...` path (`apps/catalog/media_utils.py` server-side, `composables/useMediaUrl.ts` client-side). Three layers map that prefix onto Django, in the order they take effect: nginx (`nginx/prod.conf`, `nginx/conf.d/default.conf`, serving the shared `media_data` volume with a proxy fallback), the Liara edge proxy, and — when neither is in front — `frontend/server/routes/media/[...path].ts`, a Nitro proxy that resolves its target *at request time* from `NUXT_MEDIA_PROXY` or `NUXT_API_INTERNAL_URL` (never from build-time env, which would bake in the build machine's host). `nuxt dev` has no nginx at all, so that server route is what makes images work locally. Two commands diagnose the two failure modes: `python manage.py check_media` finds DB rows whose files are missing from `MEDIA_ROOT` (volume out of sync with the database), and `curl -I http://localhost:3000/media/<path>` shows whether the routing layer is doing its job. `apps/catalog/tests_media.py` locks the relative-path contract.

**Payment flow (Zarinpal):** `ZARINPAL_SANDBOX=True` generates `MOCK_<order_number>` authority with no real HTTP call. On success: stock decremented, `sales_count` incremented, coupon usage recorded, cart cleared — all in `@transaction.atomic`.

**Dev database toggle:** `USE_SQLITE=True` (default without Docker) → SQLite + `LocMemCache`. `USE_SQLITE=False` → PostgreSQL + Redis. Docker always sets `USE_SQLITE=False`.

**Django admin:** Jazzmin theme, RTL via `static/admin/css/rtl.css`. App list grouping and dashboard stats monkey-patched in `config/urls.py`. `ProductImage.save()` auto-resizes to max 1200 px wide via Pillow.

**admin_api:** All views require `IsAdminUser` (staff). Mounted at `/api/admin/`. Covers dashboard stats, products, categories, brands, orders, users, coupons, blog, reviews, instagram, settings.

### Frontend (`frontend/`)

Nuxt 3 SSR app. Persian/RTL throughout (`lang="fa"`, `dir="rtl"`). Vazirmatn font from CDN. DaisyUI component library with custom `lumia` theme (gold/dark/cream palette).

**Dual API URL pattern** (`composables/useApi.ts`): SSR requests use `NUXT_API_INTERNAL_URL` (`http://backend:8000/api`); browser requests use `NUXT_PUBLIC_API_BASE` (dev: `http://localhost:3000/api` via devProxy; prod: `https://yourdomain.com/api`). Always use `apiFetch` from `useApi()` — never call `$fetch` directly.

**JWT expiry check:** `useApi.ts` decodes the JWT `exp` claim before attaching the `Authorization` header. Expired tokens trigger `auth.logout()` silently instead of sending the bad token (which would cause 401 even on `AllowAny` endpoints).

**Auth state:** `stores/auth.ts` (Pinia). `plugins/auth.client.ts` calls `auth.loadFromStorage()` on client mount — auth state is never available during SSR. Tokens stored in `localStorage` under keys `lumia_access`, `lumia_refresh`, `lumia_user`.

**Hydration mismatches:** Any template that branches on auth state (`isAuthenticated`, `user?.is_staff`) must be wrapped in `<ClientOnly>` with a `#fallback` slot showing the unauthenticated default. Failing to do this causes Vue hydration warnings and broken rendering.

**Vue admin dashboard:** `layouts/admin.vue` + `pages/admin/**`. Protected by `middleware/admin-auth.ts` (redirects non-staff to `/`). Sidebar is a sliding drawer on mobile (`translate-x-full lg:translate-x-0`), always visible on desktop. All list pages use a dual layout: mobile cards (`lg:hidden`) + desktop table (`hidden lg:block`).

**Admin API calls:** Admin pages call `/api/admin/*` endpoints via `apiFetch`. The `admin_api` app enforces `IsAdminUser` on every view.

**Key components:**
- `CartDrawer.vue` — slide-over cart (only fetched when `auth.isAuthenticated`)
- `LiveSearch.vue` — debounced `/api/products/search/?q=`
- `FilterSidebar.vue` — category/brand/price filters for shop page
- `MegaMenu.vue` — full category tree dropdown; loads with `{ lazy: true, server: false }` and falls back to static categories if API fails

**Sitemap:** sourced from `/api/__sitemap__/urls` (`apps/catalog/sitemap.py`). Excludes `/account`, `/cart`, `/checkout`, `/auth`.

### Environment variables

| Variable | Purpose |
|---|---|
| `USE_SQLITE` | `True` = SQLite dev mode (no Postgres/Redis needed) |
| `ZARINPAL_SANDBOX` | `True` = mock payment, no real API calls |
| `ADMIN_BYPASS_PHONE` | Single phone that logs in with any password (leave empty in production) |
| `ADMIN_PHONES` | Comma-separated phones auto-promoted to staff/superuser on boot and at registration |
| `OWNER_PHONE` / `OWNER_NAME` | Store owner shown to customers; seeds the `StoreSettings.contact_*` fields |
| `PENDING_ORDER_EXPIRY_DAYS` | Days before an unconfirmed order is cancelled (default `7`) |
| `NUXT_API_INTERNAL_URL` | Backend URL for Nuxt SSR (Docker: `http://backend:8000/api`) |
| `NUXT_PUBLIC_API_BASE` | Backend URL for browser JS (dev Docker: `http://localhost:3000/api`) |
| `GUNICORN_WORKERS` | Gunicorn worker count (default `2` in production compose) |

### Hot reload (Docker dev overlay)

Frontend: `CHOKIDAR_USEPOLLING=true` + `vite.server.watch.usePolling` in `nuxt.config.ts` handles file watching inside Docker. Access frontend at http://localhost:3000.

Backend: Django `runserver` auto-reloads on file changes via the `./backend:/app` volume mount in `docker-compose.dev.yml`.
