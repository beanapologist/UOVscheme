# Stripe setup for SilentVerify

## Live (production) — current state

| Item | Value |
|------|--------|
| Product | SilentVerify Pro (`prod_Uonndeur2RwLXN`) |
| Price | $9/mo (`price_1TpABkEWOkqksVfIXhEK0kxf`) |
| Webhook | `https://silentverify.up.railway.app/api/v1/billing/webhook` |
| Local config | `impl/python/.env` (gitignored) |

**Railway status:** `stripe_enabled` is still `false` until you set env vars on Railway (see below).

---

## 1. Wire Railway (live)

```bash
railway login
cd impl/python
railway link          # select silentverify project
./scripts/railway_set_stripe.sh
```

Or paste manually in [Railway → Variables](https://railway.app) (see `railway.stripe.vars.example`).

Also mount a **Volume** at `/app/data` and set `SILENTVERIFY_USAGE_DB=/app/data/silentverify_usage.db`.

Verify after redeploy:

```bash
curl -s https://silentverify.up.railway.app/api/v1/billing/status
# expect "stripe_enabled": true
```

---

## 2. Test mode (local, no real charges)

1. [Stripe Dashboard → Test mode](https://dashboard.stripe.com/test/apikeys) → copy `sk_test_…` and `pk_test_…`
2. Copy env templates:

```bash
cp impl/python/.env.test.example impl/python/.env.test
cp silent-verify-client/.env.test.example silent-verify-client/.env.test.local
```

3. Add your test keys to those files.
4. Bootstrap test product + price:

```bash
cd impl/python
./scripts/stripe_bootstrap.sh test
```

5. Local webhook (test mode supports `stripe listen`):

```bash
stripe listen --forward-to localhost:8765/api/v1/billing/webhook
# copy whsec_... into impl/python/.env.test
```

6. Run API in test mode + client:

```bash
# Terminal 1
cd impl/python
SILENTVERIFY_STRIPE_MODE=test ./run_saas.sh

# Terminal 2
cd silent-verify-client
cp .env.test.local .env.local   # or merge pk_test into .env.local
npm run client
```

Test card: `4242 4242 4242 4242`, any future expiry/CVC.

---

## 3. Checkout flow

1. User clicks **Subscribe with Stripe** on homepage
2. `POST /api/v1/billing/checkout` → Stripe hosted checkout
3. Stripe webhook `checkout.session.completed` → API provisions Pro key
4. Redirect to `/?checkout=success&session_id=…` → Next.js redeems key

**Note:** `SILENTVERIFY_PUBLIC_URL` must be the URL where users land after payment (your Next.js frontend). If the frontend is not on Railway, set it to that host instead of the API URL.

---

## Scripts

| Script | Purpose |
|--------|---------|
| `scripts/stripe_bootstrap.sh live\|test` | Create product/price (+ optional webhook) |
| `scripts/railway_set_stripe.sh` | Push `.env` Stripe vars to Railway |
