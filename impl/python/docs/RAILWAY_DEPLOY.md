# Deploy SilentVerify API on Railway

Production deployment uses **real UOV signing** (`SILENTVERIFY_UOV_PROFILE=I_MIN`), SQLite usage DB, optional **Stripe** billing, and the landing page at `/`.

## 1. Create Railway project

1. [railway.app](https://railway.app) → **New Project** → **Deploy from GitHub repo** → `beanapologist/UOVscheme`.
2. Set **Root Directory** to `impl/python`.
3. Railway reads `railway.json`; Nixpacks installs Python from `requirements.txt` (→ `requirements-saas.txt`) and runs `uvicorn api.app:app`.

## 2. Required variables

| Variable | Example | Purpose |
|----------|---------|---------|
| `SILENTVERIFY_ENV` | `production` | No default dev API key; uses `I_MIN` UOV profile |
| `SILENTVERIFY_ISSUER_SEED` | *(random int)* | Deterministic issuer secret — **change from 42** |
| `SILENTVERIFY_PUBLIC_URL` | `https://your-app.up.railway.app` | Stripe redirects + OpenAPI links |
| `SILENTVERIFY_UOV_PROFILE` | `I_MIN` | Production parameter set |

## 3. Stripe (Pro subscriptions)

1. [Stripe Dashboard](https://dashboard.stripe.com) → **Products** → add **Pro** at $9/mo → copy **Price ID** (`price_…`).
2. **Developers → Webhooks** → endpoint  
   `https://your-app.up.railway.app/api/v1/billing/webhook`  
   Events: `checkout.session.completed`
3. Set on Railway:

| Variable | Value |
|----------|--------|
| `STRIPE_SECRET_KEY` | `sk_live_…` or `sk_test_…` |
| `STRIPE_WEBHOOK_SECRET` | `whsec_…` |
| `STRIPE_PRICE_ID` | `price_…` |

4. Visit `/` → **Subscribe with Stripe** → after payment, API key is shown once.

Free keys: **Get free API key** on `/` (no Stripe).

## 4. Persistent SQLite (recommended)

Add a **Volume** mounted at `/app/data` (or your service path) and set:

```bash
SILENTVERIFY_USAGE_DB=/app/data/silentverify_usage.db
```

## 5. Optional

```bash
SILENTVERIFY_PRO_MONTHLY_QUOTA=100000
SILENTVERIFY_CORS_ORIGIN=https://your-frontend.com
```

## 6. Verify

```bash
curl https://your-app.up.railway.app/api/v1/health
open https://your-app.up.railway.app/
open https://your-app.up.railway.app/docs    # Try API console (use cases)
open https://your-app.up.railway.app/swagger # Advanced OpenAPI UI
```

Get an API key from `/` (free or Stripe), then paste it into the **Try API** page or **Authorize** in Swagger.
