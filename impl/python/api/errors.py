"""Human-readable API error hints for chain and validation failures."""

from __future__ import annotations

import re
from typing import Any, Dict, Optional

# (substring in lowercased message, hint). First match wins.
_HINTS: tuple[tuple[str, str], ...] = (
    (
        "loopback",
        "Public RPC URLs only in production. For local Hardhat/Anvil, set SILENTVERIFY_ALLOW_LOOPBACK_RPC=1 on the server.",
    ),
    (
        "127.0.0.1",
        "This deployment blocks loopback RPC URLs. Use a public HTTPS endpoint or enable loopback for local dev.",
    ),
    (
        "rpc_url must use http",
        "Use a full HTTPS RPC URL (e.g. from Alchemy, Infura, or drpc). See GET /api/v1/chains/evm/hints.",
    ),
    (
        "rpc_url must include",
        "Paste the full RPC URL including hostname, not just a chain name.",
    ),
    (
        "depth",
        "The on-chain anchor did not match the certificate within your depth policy — try a higher reorg depth or re-issue at a newer block.",
    ),
    (
        "reorg",
        "Chain head moved since issuance. Re-fetch the anchor with a higher depth policy or issue a fresh certificate.",
    ),
    (
        "stale",
        "RPC returned data older than expected. Retry with an explicit block height or a different RPC provider.",
    ),
    (
        "403",
        "RPC provider rejected the request (often missing API key or User-Agent). Add rpc_headers with your provider key.",
    ),
    (
        "401",
        "RPC authentication failed — check your provider API key in rpc_headers.",
    ),
    (
        "connection failed",
        "Could not reach the RPC host. Check the URL, firewall, and that the provider allows server-side calls.",
    ),
    (
        "http ",
        "RPC HTTP error from the node — verify the URL, network, and that the block/slot/height exists.",
    ),
    (
        "signature_or_fingerprint",
        "Certificate failed cryptographic verify — wrong key, tampered wire JSON, or mismatched cert_type.",
    ),
    (
        "quota_exceeded",
        "Monthly issuance quota reached. Upgrade to Pro on the home page or wait until next month.",
    ),
    (
        "missing_api_key",
        "Send your API key in the X-API-Key header (get one free at /).",
    ),
    (
        "invalid api key",
        "Unknown API key — generate a new one at / or check for typos in X-API-Key.",
    ),
    (
        "stripe_not_configured",
        "Paid checkout is not enabled on this deployment. Use Get free API key on the home page.",
    ),
    (
        "vinegar",
        "UOV parameter mismatch — ensure issuer and verifier use the same field profile (I_MIN vs TOY).",
    ),
    (
        "allow_toy_params",
        "Toy UOV parameters are disabled in production. Use profile I_MIN or contact the operator.",
    ),
    (
        "policy.",
        "Check your policy object (e.g. reorg depth) — see GET /api/v1/params and chain route examples.",
    ),
    (
        "cert_type",
        "Use the matching verify route: agent certs → /certs/agent/verify, state certs → /certs/state/verify.",
    ),
)


def hint_for_message(message: str) -> Optional[str]:
    low = message.lower()
    for needle, hint in _HINTS:
        if needle in low:
            return hint
    if re.search(r"\bhttp \d{3}\b", low):
        return _HINTS[10][1]  # RPC HTTP error
    return None


def error_detail(
    *,
    error: str,
    message: str,
    hint: Optional[str] = None,
    extra: Optional[Dict[str, Any]] = None,
) -> Dict[str, Any]:
    out: Dict[str, Any] = {"error": error, "message": message}
    h = hint or hint_for_message(message)
    if h:
        out["hint"] = h
    if extra:
        out.update(extra)
    return out
