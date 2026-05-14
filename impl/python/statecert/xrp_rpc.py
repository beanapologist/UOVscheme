"""Fetch :class:`XrpLedgerCommitment` from a rippled-compatible JSON-RPC server (stdlib only)."""

from __future__ import annotations

from typing import Any, Dict, Union

from .jsonrpc import jsonrpc_call
from .state_hash import XrpLedgerCommitment

LedgerArg = Union[int, str]


def _normalize_ledger_hash(h: str) -> str:
    s = h.strip()
    if s.startswith("0x") or s.startswith("0X"):
        body = s[2:]
    else:
        body = s
    body = body.lower()
    if len(body) != 64:
        raise ValueError("ledger_hash must be 64 hex characters")
    return "0x" + body


def fetch_xrp_ledger_commitment(
    rpc_url: str,
    *,
    network_id: str,
    ledger_index: LedgerArg = "validated",
    timeout: float = 30.0,
) -> XrpLedgerCommitment:
    """Call ``ledger``; store ``network_id`` verbatim (caller-chosen stable id, e.g. ``xrpl-mainnet``).

    ``ledger_index`` may be ``validated``, ``current``, ``closed``, or a non-negative integer.
    """
    params: Dict[str, Any] = {
        "transactions": False,
        "expand": False,
        "binary": False,
    }
    if isinstance(ledger_index, int):
        if ledger_index < 0:
            raise ValueError("ledger_index int must be non-negative")
        params["ledger_index"] = ledger_index
    else:
        s = str(ledger_index).strip()
        if not s:
            raise ValueError("ledger_index string must be non-empty")
        params["ledger_index"] = s

    res = jsonrpc_call(rpc_url, "ledger", [params], timeout=timeout)
    if not isinstance(res, dict):
        raise ValueError(f"unexpected ledger result type: {type(res).__name__}")
    led = res.get("ledger")
    if isinstance(led, dict):
        li = led.get("ledger_index")
        lh = led.get("ledger_hash")
    else:
        li = res.get("ledger_index")
        lh = res.get("ledger_hash")
    if isinstance(li, str) and li.isdigit():
        li = int(li)
    if not isinstance(li, int):
        raise ValueError("ledger response missing integer ledger_index")
    if not isinstance(lh, str):
        raise ValueError("ledger response missing ledger_hash string")
    return XrpLedgerCommitment(
        network_id=network_id.strip(),
        ledger_index=int(li),
        ledger_hash_hex=_normalize_ledger_hash(lh),
    )
