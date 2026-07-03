# Deploy SilentVerify Client (Next.js)

The **new UI** lives in `silent-verify-client/`. Railway (`impl/python`) only deploys the Python API + legacy static HTML — you need a **separate frontend deployment** for this app.

## Architecture

```
https://your-frontend.vercel.app   →  silent-verify-client (Next.js)
https://silentverify.up.railway.app →  impl/python (FastAPI API only)
```

---

## Option A: Vercel (recommended)

1. [vercel.com/new](https://vercel.com/new) → Import **beanapologist/UOVscheme**
2. **Root Directory:** `silent-verify-client`
3. Framework: **Next.js** (auto-detected; `vercel.json` included)
4. **Environment variables** (Production):

| Variable | Value |
|----------|--------|
| `NEXT_PUBLIC_API_URL` | `https://silentverify.up.railway.app` |
| `NEXT_PUBLIC_OPENAPI_URL` | `https://silentverify.up.railway.app/openapi.json` |
| `NEXT_PUBLIC_APP_URL` | `https://<your-vercel-domain>.vercel.app` |
| `NEXT_PUBLIC_STRIPE_PUBLISHABLE_KEY` | `pk_live_...` |

5. Deploy → copy your Vercel URL

### Update Railway (API) to match

In Railway → `impl/python` service → Variables:

```env
SILENTVERIFY_PUBLIC_URL=https://<your-vercel-domain>.vercel.app
SILENTVERIFY_CORS_ORIGIN=https://<your-vercel-domain>.vercel.app
```

Redeploy Railway. Stripe checkout success redirects to your Vercel homepage.

---

## Option B: Railway (second service)

1. Railway → **New Service** → same repo `beanapologist/UOVscheme`
2. **Root Directory:** `silent-verify-client`
3. Uses `silent-verify-client/railway.json`
4. Set the same `NEXT_PUBLIC_*` env vars as Vercel above
5. Set `NEXT_PUBLIC_APP_URL` to the Railway-generated frontend URL
6. Update API service `SILENTVERIFY_PUBLIC_URL` + `SILENTVERIFY_CORS_ORIGIN` to that URL

---

## Verify

```bash
# Frontend loads
open https://<your-frontend-url>

# API reachable from browser (CORS)
curl -s https://silentverify.up.railway.app/api/v1/billing/status

# Stripe enabled on API
# expect "stripe_enabled": true after Railway env vars set
```

Homepage → **Plans** → **Subscribe with Stripe** should redirect to Stripe and return with a Pro API key.

---

## Local development

```bash
cd impl/python && ./run_saas.sh
cd silent-verify-client && cp .env.example .env.local && yarn dev
```

See `.env.example` (local) and `.env.production.example` (hosted).
