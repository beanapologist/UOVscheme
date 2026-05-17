"""Billing: free keys, Stripe Checkout, webhooks."""

from __future__ import annotations

from typing import Any, Dict, Optional

from fastapi import APIRouter, Depends, HTTPException, Request

from . import auth, billing
from .deps import api_key_header, require_api_key

router = APIRouter(prefix="/api/v1/billing", tags=["Billing"])


@router.get("/status")
async def billing_public_status() -> Dict[str, Any]:
    return billing.billing_status()


@router.post("/free-key")
async def issue_free_key() -> Dict[str, Any]:
    """Generate a free-tier API key (shown once)."""
    try:
        return billing.create_free_api_key()
    except RuntimeError as exc:
        raise HTTPException(
            status_code=503,
            detail={
                "error": "api_key_registration_failed",
                "message": str(exc),
                "db": auth.auth_diagnostics(),
            },
        ) from exc


@router.post("/checkout")
async def start_pro_checkout() -> Dict[str, Any]:
    try:
        return billing.create_pro_checkout()
    except ValueError as e:
        if str(e) == "stripe_not_configured":
            raise HTTPException(
                status_code=503,
                detail="Stripe is not configured on this deployment (STRIPE_SECRET_KEY, STRIPE_PRICE_ID).",
            ) from e
        raise HTTPException(status_code=400, detail=str(e)) from e


@router.get("/session/{session_id}")
async def redeem_checkout_session(session_id: str) -> Dict[str, Any]:
    try:
        return billing.redeem_session(session_id)
    except ValueError as e:
        code = str(e)
        if code == "unknown_session":
            raise HTTPException(status_code=404, detail="Unknown checkout session") from e
        if code == "session_not_ready":
            raise HTTPException(status_code=409, detail="Payment not completed yet") from e
        if code == "already_revealed":
            raise HTTPException(status_code=410, detail="API key already retrieved") from e
        raise HTTPException(status_code=400, detail=code) from e


@router.post("/webhook")
async def stripe_webhook(request: Request) -> Dict[str, Any]:
    payload = await request.body()
    sig = request.headers.get("stripe-signature")
    try:
        return billing.handle_webhook(payload, sig)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e)) from e
    except Exception as e:
        msg = str(e)
        if "signature" in msg.lower():
            raise HTTPException(status_code=400, detail="invalid_stripe_signature") from e
        raise HTTPException(status_code=400, detail=f"webhook_error: {msg}") from e


@router.get("/diagnostics")
async def billing_diagnostics() -> Dict[str, Any]:
    """Public DB/auth diagnostics (no secrets). Use when API keys fail mysteriously."""
    return auth.auth_diagnostics()


@router.get("/validate-key")
async def validate_key(
    request: Request,
    x_api_key: Optional[str] = Depends(api_key_header),
) -> Dict[str, Any]:
    """Check whether an API key is registered (no quota charge)."""
    from .deps import _extract_api_key

    raw = _extract_api_key(request, x_api_key)
    try:
        kh, tier, quota = auth.validate_api_key(raw)
        return {
            "valid": True,
            "tier": tier,
            "monthly_quota": quota,
            **auth.usage_summary(kh),
            "key_prefix": auth.normalize_api_key(raw)[:12] + "…" if raw else None,
        }
    except ValueError as e:
        code = str(e)
        return {
            "valid": False,
            "error": code,
            "hint": auth.invalid_key_hint() if code == "invalid_api_key" else "Send X-API-Key header.",
            "db": auth.auth_diagnostics(),
            "key_prefix": auth.normalize_api_key(raw)[:12] + "…" if raw else None,
        }


@router.get("/usage")
async def my_usage(ctx: dict = Depends(require_api_key)) -> Dict[str, Any]:
    summary = auth.usage_summary(ctx["key_hash"])
    summary["tier"] = ctx["tier"]
    return summary
