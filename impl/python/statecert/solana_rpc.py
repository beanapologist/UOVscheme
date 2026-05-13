"""Fetch :class:`SolanaCommitment` from a Solana JSON-RPC endpoint (stdlib only)."""

from __future__ import annotations

from typing import Any, Dict

from .jsonrpc import jsonrpc_call
from .state_hash import SolanaCommitment


def fetch_solana_commitment(
    rpc_url: str,
    *,
    cluster_id: str = "mainnet-beta",
    slot: int | None = None,
    commitment: str = "finalized",
    timeout: float = 30.0,
) -> SolanaCommitment:
    """Return slot + blockhash for ``slot``, or for the current head if ``slot`` is None.

    ``cluster_id`` is stored verbatim in the anchor (e.g. ``mainnet-beta``, ``devnet``).
    It does **not** have to match the RPC host string; callers should keep it consistent
    across their deployment so digests line up with operational naming.
    """
    if slot is None:
        slot_res = jsonrpc_call(
            rpc_url, "getSlot", [{"commitment": commitment}], timeout=timeout
        )
        if not isinstance(slot_res, int):
            raise ValueError(f"unexpected getSlot result: {slot_res!r}")
        slot = slot_res

    cfg: Dict[str, Any] = {
        "encoding": "json",
        "transactionDetails": "none",
        "rewards": False,
        "commitment": commitment,
    }
    block = jsonrpc_call(rpc_url, "getBlock", [slot, cfg], timeout=timeout)
    if block is None:
        raise RuntimeError(
            f"getBlock returned null for slot {slot} (missing history or bad slot)"
        )
    if not isinstance(block, dict):
        raise ValueError(f"unexpected getBlock result type: {type(block).__name__}")
    bh = block.get("blockhash")
    if not isinstance(bh, str):
        raise ValueError("getBlock JSON missing blockhash string")
    return SolanaCommitment(cluster_id=cluster_id, slot=int(slot), blockhash_b58=bh)
