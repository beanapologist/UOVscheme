#!/usr/bin/env bash
# Push Stripe + public URL vars from impl/python/.env to Railway.
# Requires: railway CLI logged in (`railway login`) and project linked (`railway link`).
set -euo pipefail
cd "$(dirname "$0")/.."

ENV_FILE=".env"
if [[ ! -f "$ENV_FILE" ]]; then
  echo "Missing $ENV_FILE"
  exit 1
fi

set -a
# shellcheck disable=SC1090
source "$ENV_FILE"
set +a

: "${STRIPE_SECRET_KEY:?STRIPE_SECRET_KEY missing}"
: "${STRIPE_PRICE_ID:?STRIPE_PRICE_ID missing}"
: "${STRIPE_WEBHOOK_SECRET:?STRIPE_WEBHOOK_SECRET missing}"
: "${SILENTVERIFY_PUBLIC_URL:?SILENTVERIFY_PUBLIC_URL missing}"

echo "Setting Railway variables (values not printed)..."
railway variables set \
  "STRIPE_SECRET_KEY=${STRIPE_SECRET_KEY}" \
  "STRIPE_PRICE_ID=${STRIPE_PRICE_ID}" \
  "STRIPE_WEBHOOK_SECRET=${STRIPE_WEBHOOK_SECRET}" \
  "SILENTVERIFY_PUBLIC_URL=${SILENTVERIFY_PUBLIC_URL}" \
  "SILENTVERIFY_ENV=production" \
  "SILENTVERIFY_UOV_PROFILE=I_MIN" \
  "SILENTVERIFY_USAGE_DB=/app/data/silentverify_usage.db"

echo "Done. Redeploy may be required. Verify:"
echo "  curl -s https://silentverify.up.railway.app/api/v1/billing/status"
