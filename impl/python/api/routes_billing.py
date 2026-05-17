"""Billing: free keys, Stripe Checkout, webhooks."""

from __future__ import annotations

from typing import Any, Dict

from fastapi import APIRouter, Depends, HTTPException, Request

from . import auth, billing
from .deps import require_api_key

router = APIRouter(prefix="/api/v1/billing", tags=["Billing"])


@router.get("/status")
async def billing_public_status() -> Dict[str, Any]:
    return billing.billing_status()


@router.post("/free-key")
async def issue_free_key() -> Dict[str, Any]:
    """Generate a free-tier API key (shown once)."""
    return billing.create_free_api_key()


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


@router.get("/usage")
async def my_usage(ctx: dict = Depends(require_api_key)) -> Dict[str, Any]:
    summary = auth.usage_summary(ctx["key_hash"])
    summary["tier"] = ctx["tier"]
    return summary
