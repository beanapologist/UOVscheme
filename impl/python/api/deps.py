"""FastAPI dependencies."""

from __future__ import annotations

import os
from typing import Optional

from fastapi import Depends, HTTPException
from fastapi.security import APIKeyHeader

from . import auth
from .errors import error_detail

# Registers ``X-API-Key`` in OpenAPI → Swagger **Authorize** button.
api_key_header = APIKeyHeader(
    name="X-API-Key",
    auto_error=False,
    description="Dev default when using ./run_saas.sh: sv_dev_test_key",
)


def require_api_key(x_api_key: Optional[str] = Depends(api_key_header)):
    try:
        key_hash, tier, quota = auth.validate_api_key(x_api_key)
    except ValueError as e:
        code = str(e)
        if code == "missing_api_key":
            raise HTTPException(
                status_code=401,
                detail=error_detail(error="missing_api_key", message="X-API-Key header required"),
            ) from e
        raise HTTPException(
            status_code=403,
            detail=error_detail(error="invalid_api_key", message="Unknown or revoked API key"),
        ) from e
    return {"key_hash": key_hash, "tier": tier, "quota": quota}


def enforce_issue_quota(ctx: dict) -> None:
    try:
        auth.check_and_record_usage(ctx["key_hash"], "issue", ctx["quota"])
    except ValueError as e:
        if str(e) == "quota_exceeded":
            usage = auth.usage_summary(ctx["key_hash"])
            raise HTTPException(
                status_code=429,
                detail=error_detail(
                    error="quota_exceeded",
                    message=(
                        f"Monthly issuance limit reached "
                        f"({usage['issue_certs_used']}/{usage['issue_certs_quota']})."
                    ),
                    extra={"usage": usage},
                ),
            ) from e
        raise


def cors_origins() -> list[str]:
    raw = os.environ.get("SILENTVERIFY_CORS_ORIGIN", "*")
    if raw == "*":
        return ["*"]
    return [o.strip() for o in raw.split(",") if o.strip()]
