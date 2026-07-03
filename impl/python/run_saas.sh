#!/usr/bin/env bash
# Start SilentVerify SaaS API (macOS-friendly: uses python3 -m).
set -euo pipefail
cd "$(dirname "$0")"

if [[ "${SILENTVERIFY_STRIPE_MODE:-}" == "test" && -f .env.test ]]; then
  set -a
  # shellcheck disable=SC1091
  source .env.test
  set +a
  echo "Stripe mode: TEST (.env.test)"
elif [[ -f .env ]]; then
  set -a
  # shellcheck disable=SC1091
  source .env
  set +a
  echo "Stripe mode: LIVE (.env)"
fi

export SILENTVERIFY_UOV_PROFILE="${SILENTVERIFY_UOV_PROFILE:-TOY}"
export SILENTVERIFY_API_KEYS="${SILENTVERIFY_API_KEYS:-free:sv_dev_test_key}"
export SILENTVERIFY_DEV_API_KEY="${SILENTVERIFY_DEV_API_KEY:-sv_dev_test_key}"
export SILENTVERIFY_PUBLIC_URL="${SILENTVERIFY_PUBLIC_URL:-http://localhost:3000}"

python3 -m pip install -q -r requirements-saas.txt
echo "SilentVerify API → http://127.0.0.1:8765/docs"
echo "API key header: X-API-Key: sv_dev_test_key"
exec python3 -m uvicorn api.app:app --reload --host 127.0.0.1 --port 8765
