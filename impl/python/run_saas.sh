#!/usr/bin/env bash
# Start SilentVerify SaaS API (macOS-friendly: uses python3 -m).
set -euo pipefail
cd "$(dirname "$0")"

export SILENTVERIFY_UOV_PROFILE="${SILENTVERIFY_UOV_PROFILE:-TOY}"
export SILENTVERIFY_API_KEYS="${SILENTVERIFY_API_KEYS:-free:sv_dev_test_key}"
export SILENTVERIFY_DEV_API_KEY="${SILENTVERIFY_DEV_API_KEY:-sv_dev_test_key}"

python3 -m pip install -q -r requirements-saas.txt
echo "SilentVerify API → http://127.0.0.1:8765/docs"
echo "API key header: X-API-Key: sv_dev_test_key"
exec python3 -m uvicorn api.app:app --reload --host 127.0.0.1 --port 8765
