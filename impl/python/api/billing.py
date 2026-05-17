"""Stripe Checkout + API key provisioning."""

from __future__ import annotations

import os
import secrets
from typing import Any, Dict, Optional

from . import auth

_STRIPE_SECRET = os.environ.get("STRIPE_SECRET_KEY", "").strip()
_STRIPE_WEBHOOK = os.environ.get("STRIPE_WEBHOOK_SECRET", "").strip()
_STRIPE_PRICE = os.environ.get("STRIPE_PRICE_ID", "").strip()
_PUBLIC_URL = os.environ.get("SILENTVERIFY_PUBLIC_URL", "http://127.0.0.1:8765").rstrip("/")


def stripe_enabled() -> bool:
    return bool(_STRIPE_SECRET and _STRIPE_PRICE)


def _stripe():
    import stripe

    stripe.api_key = _STRIPE_SECRET
    return stripe


def create_pro_checkout() -> Dict[str, Any]:
    if not stripe_enabled():
        raise ValueError("stripe_not_configured")
    stripe = _stripe()
    session = stripe.checkout.Session.create(
        mode="subscription",
        line_items=[{"price": _STRIPE_PRICE, "quantity": 1}],
        success_url=f"{_PUBLIC_URL}/?checkout=success&session_id={{CHECKOUT_SESSION_ID}}",
        cancel_url=f"{_PUBLIC_URL}/?checkout=cancelled",
        metadata={"product": "silentverify_pro"},
    )
    auth.save_checkout_session(session.id, tier="pro", status="pending")
    return {"checkout_url": session.url, "session_id": session.id}


def handle_webhook(payload: bytes, sig_header: Optional[str]) -> Dict[str, Any]:
    if not _STRIPE_SECRET or not _STRIPE_WEBHOOK:
        raise ValueError("stripe_webhook_not_configured")
    stripe = _stripe()
    event = stripe.Webhook.construct_event(payload, sig_header, _STRIPE_WEBHOOK)
    if event["type"] == "checkout.session.completed":
        sess = event["data"]["object"]
        session_id = sess["id"]
        customer = sess.get("customer")
        api_key = auth.provision_key_for_checkout(
            session_id,
            tier="pro",
            stripe_customer_id=str(customer) if customer else None,
        )
        return {"handled": True, "session_id": session_id, "provisioned": bool(api_key)}
    return {"handled": False, "type": event["type"]}


def redeem_session(session_id: str) -> Dict[str, Any]:
    row = auth.get_checkout_session(session_id)
    if not row:
        raise ValueError("unknown_session")
    if row["status"] != "completed" or not row.get("api_key_plain"):
        raise ValueError("session_not_ready")
    key = auth.reveal_checkout_key(session_id)
    return {
        "tier": row["tier"],
        "api_key": key,
        "message": "Store this key securely — it is shown only once.",
    }


def create_free_api_key() -> Dict[str, Any]:
    key = "sv_free_" + secrets.token_urlsafe(18)
    auth.register_api_key(key, tier="free", label="free_signup")
    try:
        auth.validate_api_key(key)
    except ValueError as exc:
        raise RuntimeError(
            "api_key_registration_failed — SQLite may not be writable; "
            "set SILENTVERIFY_USAGE_DB on a Railway volume. "
            + str(auth.auth_diagnostics())
        ) from exc
    return {
        "tier": "free",
        "api_key": key,
        "monthly_quota": auth.DEFAULT_FREE_MONTHLY,
        "message": "Free tier: 100 certificate issuances per month.",
        "db": auth.auth_diagnostics(),
    }


def billing_status() -> Dict[str, Any]:
    return {
        "stripe_enabled": stripe_enabled(),
        "public_url": _PUBLIC_URL,
        "plans": {
            "free": {"price_usd": 0, "quota_per_month": auth.DEFAULT_FREE_MONTHLY},
            "pro": {
                "price_usd": 9,
                "quota_per_month": int(
                    os.environ.get("SILENTVERIFY_PRO_MONTHLY_QUOTA", "100000")
                ),
                "stripe_required": True,
            },
        },
    }
