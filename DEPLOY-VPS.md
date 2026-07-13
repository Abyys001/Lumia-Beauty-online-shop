# Deploy to a VPS — lumiabeauty.ir (prebuilt images + Let's Encrypt SSL)

Single-server Docker Compose deployment: **db + redis + backend + frontend + nginx + certbot**.
Images are **built and pushed from your machine**, then **pulled** on the server — the server
never compiles anything.

```
your machine                          VPS (Ubuntu)
────────────                          ─────────────────────────────
build-and-push.sh  ──►  registry  ──►  docker compose pull
                                       nginx (:80/:443, TLS)
                                        ├─ /api /django-admin /static /media → backend:8000
                                        └─ everything else                   → frontend:3000
```

## 0. Prerequisites

- A VPS with a public IP (Iran-based recommended for Zarinpal/SMS latency + access).
- DNS **A records** for `lumiabeauty.ir` and `www.lumiabeauty.ir` → the VPS IP.
- Ports **80** and **443** open in the firewall.
- A registry account (Docker Hub `siavashdev`, or override `REGISTRY`).

Verify DNS before requesting a cert:
```bash
dig +short lumiabeauty.ir      # must return the VPS IP
dig +short www.lumiabeauty.ir
```

## 1. Build & push images (on your machine)

```bash
docker login                       # to docker.io/siavashdev
./scripts/build-and-push.sh
```
Produces `siavashdev/lumia-backend:latest` and `siavashdev/lumia-frontend:latest`
(frontend uses `Dockerfile.prod`, which runs `npm run build` inside the image).

## 2. Prepare the server

Install Docker Engine + compose plugin (Ubuntu):
```bash
curl -fsSL https://get.docker.com | sh
```

Get the repo onto the server and set the environment file:
```bash
git clone <your-repo-url> lumia && cd lumia
cp .env.vps .env
```

Then **edit `.env`** and fill in the real values (these are placeholders in `.env.vps`):

| Must set | Notes |
|---|---|
| `DJANGO_SECRET_KEY` | Generate a **new** one — do not reuse the sample. |
| `ZARINPAL_MERCHANT_ID` | Real Zarinpal merchant id; keep `ZARINPAL_SANDBOX=False`. |
| `IRANPAYAMAK_API_KEY` / line / pattern | Real SMS credentials, or switch `SMS_PROVIDER`. |
| `POSTGRES_PASSWORD` | Change from the sample value. |

Already correct for this domain: `DJANGO_ALLOWED_HOSTS`, `CSRF_TRUSTED_ORIGINS`,
`CORS_ALLOWED_ORIGINS`, `NUXT_PUBLIC_API_BASE`, `NUXT_PUBLIC_SITE_URL`, callback URL.

Generate a fresh secret key:
```bash
python3 -c "import secrets; print(secrets.token_urlsafe(64))"
```

## 3. Pull images

```bash
docker compose pull
```
(If you changed `REGISTRY`/`TAG`, set `BACKEND_IMAGE`/`FRONTEND_IMAGE` in `.env` to match.)

## 4. Obtain the SSL certificate (one time)

```bash
./scripts/init-letsencrypt.sh
```
This boots nginx with a temporary self-signed cert, then swaps in a real
Let's Encrypt cert for both domains. Test first with `staging=1` inside the
script if you want to avoid rate limits, then rerun with `staging=0`.

## 5. Bring the whole stack up

```bash
docker compose -f docker-compose.yml -f docker-compose.prod.yml up -d
```

The backend entrypoint auto-runs `migrate` and `collectstatic` on start
(because `APP_ENV=production`). Create an admin user:
```bash
docker compose exec backend python manage.py createsuperuser
```

Visit **https://lumiabeauty.ir** — HTTP redirects to HTTPS automatically.

## Operations

**Renewals** are automatic: the `certbot` container retries every 12h and nginx
reloads every 6h, so certs renew ~30 days before expiry with no action needed.

**Deploy a new version:**
```bash
# machine:
./scripts/build-and-push.sh
# server:
docker compose pull && \
  docker compose -f docker-compose.yml -f docker-compose.prod.yml up -d
```

**Logs / status:**
```bash
docker compose -f docker-compose.yml -f docker-compose.prod.yml ps
docker compose logs -f nginx
docker compose logs -f backend
```

**Postgres backup:**
```bash
docker compose exec db pg_dump -U lumia lumia_beauty > backup_$(date +%F).sql
```

## Notes & gotchas

- **No app ports are exposed publicly** — only nginx (80/443). `db`, `redis`,
  `backend`, `frontend` talk over the internal `lumia_net` bridge.
- `SECURE_PROXY_SSL_HEADER` is already set in Django settings, and nginx sends
  `X-Forwarded-Proto`, so `SECURE_SSL_REDIRECT=True` will not cause a redirect loop.
- Static files are shared with nginx via the `static_data` volume (collectstatic
  writes to `/app/staticfiles`); media via `media_data`. Both fall back to Django
  if a file is missing.
- `cp .env.vps .env` is required — Compose reads `.env`, not `.env.vps`.
