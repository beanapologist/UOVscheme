#!/usr/bin/env bash
# Bootstrap Stripe product + price + (optional) webhook for SilentVerify.
# Usage:
#   ./scripts/stripe_bootstrap.sh live   # uses impl/python/.env
#   ./scripts/stripe_bootstrap.sh test   # uses impl/python/.env.test
set -euo pipefail
cd "$(dirname "$0")/.."

MODE="${1:-}"
if [[ "$MODE" != "live" && "$MODE" != "test" ]]; then
  echo "Usage: $0 live|test"
  exit 1
fi

ENV_FILE=".env"
if [[ "$MODE" == "test" ]]; then
  ENV_FILE=".env.test"
fi

if [[ ! -f "$ENV_FILE" ]]; then
  echo "Missing $ENV_FILE — copy from ${ENV_FILE}.example and add your sk_${MODE}_ key."
  exit 1
fi

set -a
# shellcheck disable=SC1090
source "$ENV_FILE"
set +a

if [[ -z "${STRIPE_SECRET_KEY:-}" ]]; then
  echo "STRIPE_SECRET_KEY not set in $ENV_FILE"
  exit 1
fi

echo "==> Creating SilentVerify Pro product + \$9/mo price ($MODE mode)..."
PRICE_JSON=$(stripe prices create --api-key "$STRIPE_SECRET_KEY" \
  -d "unit_amount=900" \
  -d "currency=usd" \
  -d "recurring[interval]=month" \
  -d "product_data[name]=SilentVerify Pro" \
  -d "product_data[description]=Pro API tier ($MODE)")

PRICE_ID=$(echo "$PRICE_JSON" | python3 -c "import sys,json; print(json.load(sys.stdin)['id'])")
echo "    STRIPE_PRICE_ID=$PRICE_ID"

if grep -q '^STRIPE_PRICE_ID=' "$ENV_FILE"; then
  sed -i.bak "s|^STRIPE_PRICE_ID=.*|STRIPE_PRICE_ID=$PRICE_ID|" "$ENV_FILE"
  rm -f "${ENV_FILE}.bak"
else
  echo "STRIPE_PRICE_ID=$PRICE_ID" >> "$ENV_FILE"
fi

if [[ -n "${WEBHOOK_URL:-}" ]]; then
  echo "==> Creating webhook endpoint → $WEBHOOK_URL"
  WH_JSON=$(stripe webhook_endpoints create --api-key "$STRIPE_SECRET_KEY" \
    -d "url=${WEBHOOK_URL}" \
    -d "enabled_events[]=checkout.session.completed")
  WHSEC=$(echo "$WH_JSON" | python3 -c "import sys,json; print(json.load(sys.stdin)['secret'])")
  echo "    STRIPE_WEBHOOK_SECRET=$WHSEC"
  if grep -q '^STRIPE_WEBHOOK_SECRET=' "$ENV_FILE"; then
    sed -i.bak "s|^STRIPE_WEBHOOK_SECRET=.*|STRIPE_WEBHOOK_SECRET=$WHSEC|" "$ENV_FILE"
    rm -f "${ENV_FILE}.bak"
  else
    echo "STRIPE_WEBHOOK_SECRET=$WHSEC" >> "$ENV_FILE"
  fi
fi

echo ""
echo "Done. Updated $ENV_FILE"
echo "Verify: curl -s \${NEXT_PUBLIC_API_URL:-http://127.0.0.1:8765}/api/v1/billing/status"
