"""Server-side helpers: validate public HTTP(S) URLs, fetch live anchors, bind state certificates."""

from __future__ import annotations

import ipaddress
import os
from typing import Any, Dict, List, Optional, Union

from .certificate import StateCertificate
from .cosmos_rpc import fetch_cosmos_commitment
from .evm_rpc import BlockArg, fetch_chain_state_evm
from .jsonrpc import jsonrpc_call
from .solana_rpc import fetch_solana_commitment
from .state_hash import (
    ChainState,
    CosmosCommitment,
    CrossChainStateTransition,
    CrossL1Commitment,
    SolanaCommitment,
    XrpLedgerCommitment,
    chain_state_to_digest,
    cosmos_commitment_to_digest,
    cross_chain_to_digest,
    cross_l1_commitment_to_digest,
    solana_commitment_to_digest,
    xrp_commitment_to_digest,
)
from .xrp_rpc import LedgerArg, fetch_xrp_ledger_commitment


def _policy_leg_dict(
    pol: Optional[Dict[str, Any]], key: str
) -> Optional[Dict[str, Any]]:
    if not pol or key not in pol:
        return None
    v = pol.get(key)
    if v is None:
        return None
    if not isinstance(v, dict):
        raise ValueError(f"policy.{key} must be a JSON object or omitted")
    return v


def _allow_loopback_rpc() -> bool:
    return os.environ.get("SILENTVERIFY_ALLOW_LOOPBACK_RPC", "").lower() in (
        "1",
        "true",
        "yes",
    )


def validate_public_rpc_url(url: str) -> str:
    """Reject obvious SSRF targets (loopback / private / link-local IPs) unless env allows.

    Hostnames are accepted without DNS resolution (callers should use trusted RPC providers).
    """
    from urllib.parse import urlparse

    raw = url.strip()
    p = urlparse(raw)
    if p.scheme not in ("http", "https"):
        raise ValueError("rpc_url must use http or https")
    host = p.hostname
    if not host:
        raise ValueError("rpc_url must include a host")
    allow = _allow_loopback_rpc()
    if host.lower() == "localhost" and not allow:
        raise ValueError(
            "rpc_url host 'localhost' is blocked by default; set SILENTVERIFY_ALLOW_LOOPBACK_RPC=1 for local dev"
        )
    try:
        ip = ipaddress.ip_address(host)
    except ValueError:
        return raw
    if (
        ip.is_private or ip.is_loopback or ip.is_link_local or ip.is_reserved
    ) and not allow:
        raise ValueError(
            "rpc_url host IP is non-public; use a public RPC endpoint or set SILENTVERIFY_ALLOW_LOOPBACK_RPC=1"
        )
    return raw


def _binding_report(
    cert: StateCertificate,
    y_live: List[int],
    anchor_key: str,
    anchor_dict: Dict[str, Any],
) -> Dict[str, Any]:
    digest_match = y_live == list(cert.inner.digest_y)
    crypto_ok = cert.verify_crypto()
    full_ok = cert.verify()
    return {
        "ok": bool(digest_match and full_ok),
        "digest_binds_to_anchor": digest_match,
        "certificate_crypto_ok": crypto_ok,
        "certificate_full_ok": full_ok,
        "computed_digest_y": y_live,
        anchor_key: anchor_dict,
    }


def verify_evm_state_certificate_against_chain(
    certificate_wire: Dict[str, Any],
    chain_state: ChainState,
) -> Dict[str, Any]:
    cert = StateCertificate.from_wire_dict(certificate_wire)
    y_live = chain_state_to_digest(cert.inner.q, cert.inner.o, chain_state)
    return _binding_report(cert, y_live, "chain_state", chain_state.to_canonical_dict())


def enforce_evm_min_confirmations_behind_tip(
    rpc_url: str,
    state: ChainState,
    min_confirmations: int,
    *,
    timeout: float = 30.0,
    rpc_headers: Optional[Dict[str, str]] = None,
) -> None:
    """Require ``eth_blockNumber - state.block_height >= min_confirmations`` (same RPC).

    Use after ``fetch_chain_state_evm`` when you want a machine-checkable depth policy
    (e.g. avoid treating a head-adjacent block as settled). Omit or use ``0`` to skip.
    """
    if min_confirmations <= 0:
        return
    raw = jsonrpc_call(
        rpc_url, "eth_blockNumber", [], timeout=timeout, headers=rpc_headers
    )
    if not isinstance(raw, str) or not raw.startswith("0x"):
        raise ValueError(f"unexpected eth_blockNumber payload: {raw!r}")
    tip = int(raw, 16)
    depth = tip - int(state.block_height)
    if depth < min_confirmations:
        raise ValueError(
            f"evm policy: anchor block {state.block_height} is {depth} behind tip {tip}; "
            f"need min_confirmations_behind_tip>={min_confirmations}"
        )


def _policy_evm_depth(
    rpc_url: str,
    state: ChainState,
    policy: Optional[Dict[str, Any]],
    *,
    timeout: float,
    rpc_headers: Optional[Dict[str, str]] = None,
) -> None:
    if not policy:
        return
    if not isinstance(policy, dict):
        raise ValueError("policy leg must be a JSON object when provided")
    n = policy.get("min_confirmations_behind_tip")
    if n is None:
        return
    if type(n) is not int or n < 0:
        raise ValueError(
            "policy.min_confirmations_behind_tip must be a non-negative int"
        )
    enforce_evm_min_confirmations_behind_tip(
        rpc_url, state, n, timeout=timeout, rpc_headers=rpc_headers
    )


def verify_evm_state_certificate_via_rpc(
    rpc_url: str,
    block: BlockArg,
    certificate_wire: Dict[str, Any],
    *,
    caip2_chain_id: Optional[str] = None,
    policy: Optional[Dict[str, Any]] = None,
    timeout: float = 30.0,
    rpc_headers: Optional[Dict[str, str]] = None,
) -> Dict[str, Any]:
    safe_url = validate_public_rpc_url(rpc_url)
    state = fetch_chain_state_evm(
        safe_url,
        block=block,
        caip2_chain_id=caip2_chain_id,
        timeout=timeout,
        rpc_headers=rpc_headers,
    )
    _policy_evm_depth(
        safe_url, state, policy, timeout=timeout, rpc_headers=rpc_headers
    )
    return verify_evm_state_certificate_against_chain(certificate_wire, state)


def verify_cross_chain_state_transition_against_pair(
    certificate_wire: Dict[str, Any],
    src: ChainState,
    dst: ChainState,
) -> Dict[str, Any]:
    """Check certificate digest against a :class:`CrossChainStateTransition` (two EVM-style anchors)."""
    cert = StateCertificate.from_wire_dict(certificate_wire)
    x = CrossChainStateTransition(src=src, dst=dst)
    y_live = cross_chain_to_digest(cert.inner.q, cert.inner.o, x)
    return _binding_report(
        cert, y_live, "cross_chain_state_transition", x.to_canonical_dict()
    )


def verify_cross_chain_state_transition_via_rpc(
    certificate_wire: Dict[str, Any],
    *,
    src: Dict[str, Any],
    dst: Dict[str, Any],
    policy: Optional[Dict[str, Any]] = None,
    timeout: float = 30.0,
) -> Dict[str, Any]:
    """Fetch two EVM :class:`ChainState` anchors and verify a cross-pair certificate.

    ``src`` / ``dst`` objects must include ``rpc_url`` (string) and may include
    ``block`` (default ``latest``), ``caip2_chain_id`` (optional string).

    Optional ``policy`` shape: ``{"src": {...}, "dst": {...}}`` where each inner dict
    may contain ``min_confirmations_behind_tip`` (int) enforced with ``eth_blockNumber``
    on that leg's RPC.
    """
    if not isinstance(src, dict) or not isinstance(dst, dict):
        raise ValueError("src and dst must be objects")
    s_rpc = src.get("rpc_url")
    d_rpc = dst.get("rpc_url")
    if not isinstance(s_rpc, str) or not s_rpc.strip():
        raise ValueError("src.rpc_url must be a non-empty string")
    if not isinstance(d_rpc, str) or not d_rpc.strip():
        raise ValueError("dst.rpc_url must be a non-empty string")
    s_url = validate_public_rpc_url(s_rpc.strip())
    d_url = validate_public_rpc_url(d_rpc.strip())
    s_block: Any = src.get("block", "latest")
    d_block: Any = dst.get("block", "latest")
    if s_block is not None and not isinstance(s_block, (int, str)):
        raise ValueError("src.block must be int or string or omitted")
    if d_block is not None and not isinstance(d_block, (int, str)):
        raise ValueError("dst.block must be int or string or omitted")
    s_caip = src.get("caip2_chain_id")
    d_caip = dst.get("caip2_chain_id")
    if s_caip is not None and not isinstance(s_caip, str):
        raise ValueError("src.caip2_chain_id must be a string or omitted")
    if d_caip is not None and not isinstance(d_caip, str):
        raise ValueError("dst.caip2_chain_id must be a string or omitted")

    s_hdr = src.get("rpc_headers") if isinstance(src.get("rpc_headers"), dict) else None
    d_hdr = dst.get("rpc_headers") if isinstance(dst.get("rpc_headers"), dict) else None
    src_state = fetch_chain_state_evm(
        s_url,
        block=s_block,
        caip2_chain_id=s_caip,
        timeout=timeout,
        rpc_headers=s_hdr,
    )
    dst_state = fetch_chain_state_evm(
        d_url,
        block=d_block,
        caip2_chain_id=d_caip,
        timeout=timeout,
        rpc_headers=d_hdr,
    )
    pol = policy if isinstance(policy, dict) else None
    _policy_evm_depth(
        s_url, src_state, _policy_leg_dict(pol, "src"), timeout=timeout, rpc_headers=s_hdr
    )
    _policy_evm_depth(
        d_url, dst_state, _policy_leg_dict(pol, "dst"), timeout=timeout, rpc_headers=d_hdr
    )
    return verify_cross_chain_state_transition_against_pair(
        certificate_wire, src_state, dst_state
    )


AnchorLeg = Union[ChainState, SolanaCommitment, CosmosCommitment, XrpLedgerCommitment]


def _fetch_cross_l1_leg(
    leg: Dict[str, Any],
    *,
    side: str,
    policy_leg: Optional[Dict[str, Any]],
    timeout: float,
) -> AnchorLeg:
    """Resolve ``leg`` from JSON (``kind`` + chain-specific fields) to a typed anchor."""
    if not isinstance(leg, dict):
        raise ValueError(f"{side} must be an object")
    kind = leg.get("kind")
    if kind not in ("evm", "solana", "cosmos", "xrp"):
        raise ValueError(
            f"{side}.kind must be 'evm', 'solana', 'cosmos', or 'xrp', not {kind!r}"
        )

    if kind == "evm":
        rpc = leg.get("rpc_url")
        if not isinstance(rpc, str) or not rpc.strip():
            raise ValueError(f"{side}.rpc_url must be a non-empty string for evm")
        url = validate_public_rpc_url(rpc.strip())
        block: Any = leg.get("block", "latest")
        if block is not None and not isinstance(block, (int, str)):
            raise ValueError(f"{side}.block must be int or string or omitted")
        caip = leg.get("caip2_chain_id")
        if caip is not None and not isinstance(caip, str):
            raise ValueError(f"{side}.caip2_chain_id must be a string or omitted")
        hdr = leg.get("rpc_headers") if isinstance(leg.get("rpc_headers"), dict) else None
        state = fetch_chain_state_evm(
            url,
            block=block,
            caip2_chain_id=caip,
            timeout=timeout,
            rpc_headers=hdr,
        )
        _policy_evm_depth(url, state, policy_leg, timeout=timeout, rpc_headers=hdr)
        return state

    if kind == "solana":
        rpc = leg.get("rpc_url")
        if not isinstance(rpc, str) or not rpc.strip():
            raise ValueError(f"{side}.rpc_url must be a non-empty string for solana")
        url = validate_public_rpc_url(rpc.strip())
        cluster_id = leg.get("cluster_id", "mainnet-beta")
        if not isinstance(cluster_id, str):
            raise ValueError(f"{side}.cluster_id must be a string")
        slot = leg.get("slot")
        if slot is not None and type(slot) is not int:
            raise ValueError(f"{side}.slot must be an int or omitted")
        commitment = leg.get("commitment", "finalized")
        if not isinstance(commitment, str):
            raise ValueError(f"{side}.commitment must be a string")
        return fetch_solana_commitment(
            url,
            cluster_id=cluster_id,
            slot=slot,
            commitment=commitment,
            timeout=timeout,
        )

    if kind == "cosmos":
        rest = leg.get("rest_base")
        cid = leg.get("chain_id")
        if not isinstance(rest, str) or not rest.strip():
            raise ValueError(f"{side}.rest_base must be a non-empty string for cosmos")
        if not isinstance(cid, str) or not cid.strip():
            raise ValueError(f"{side}.chain_id must be a non-empty string for cosmos")
        safe = validate_public_rpc_url(rest.strip())
        height = leg.get("height")
        if height is not None and type(height) is not int:
            raise ValueError(f"{side}.height must be an int or omitted")
        return fetch_cosmos_commitment(
            safe, chain_id=cid.strip(), height=height, timeout=timeout
        )

    # xrp
    rpc = leg.get("rpc_url")
    if not isinstance(rpc, str) or not rpc.strip():
        raise ValueError(f"{side}.rpc_url must be a non-empty string for xrp")
    url = validate_public_rpc_url(rpc.strip())
    nid = leg.get("network_id")
    if not isinstance(nid, str) or not nid.strip():
        raise ValueError(f"{side}.network_id must be a non-empty string for xrp")
    ledger_index: Any = leg.get("ledger_index", "validated")
    if ledger_index is not None and not isinstance(ledger_index, (int, str)):
        raise ValueError(f"{side}.ledger_index must be int or string or omitted")
    return fetch_xrp_ledger_commitment(
        url,
        network_id=nid.strip(),
        ledger_index=ledger_index,
        timeout=timeout,
    )


def verify_cross_l1_commitment_against_pair(
    certificate_wire: Dict[str, Any],
    src: AnchorLeg,
    dst: AnchorLeg,
) -> Dict[str, Any]:
    """Verify a cert whose digest was built from :class:`CrossL1Commitment` (heterogeneous legs)."""
    cert = StateCertificate.from_wire_dict(certificate_wire)
    x = CrossL1Commitment(src=src, dst=dst)
    y_live = cross_l1_commitment_to_digest(cert.inner.q, cert.inner.o, x)
    return _binding_report(cert, y_live, "cross_l1_commitment", x.to_canonical_dict())


def verify_cross_l1_commitment_via_rpc(
    certificate_wire: Dict[str, Any],
    *,
    src: Dict[str, Any],
    dst: Dict[str, Any],
    policy: Optional[Dict[str, Any]] = None,
    timeout: float = 30.0,
) -> Dict[str, Any]:
    """Fetch two anchors (possibly different ecosystems) and verify a ``CrossL1`` certificate.

    Each of ``src`` / ``dst`` is an object with string ``kind``:

    * ``evm`` — ``rpc_url``, optional ``block``, ``caip2_chain_id``
    * ``solana`` — ``rpc_url``, optional ``cluster_id``, ``slot``, ``commitment``
    * ``cosmos`` — ``rest_base``, ``chain_id``, optional ``height``
    * ``xrp`` — ``rpc_url``, ``network_id``, optional ``ledger_index``

    Optional ``policy``: ``{"src": {...}, "dst": {...}}`` — only **evm** legs honor
    ``min_confirmations_behind_tip`` (same semantics as single-anchor EVM).
    """
    pol = policy if isinstance(policy, dict) else None
    src_anchor = _fetch_cross_l1_leg(
        src,
        side="src",
        policy_leg=_policy_leg_dict(pol, "src"),
        timeout=timeout,
    )
    dst_anchor = _fetch_cross_l1_leg(
        dst,
        side="dst",
        policy_leg=_policy_leg_dict(pol, "dst"),
        timeout=timeout,
    )
    return verify_cross_l1_commitment_against_pair(
        certificate_wire, src_anchor, dst_anchor
    )


def verify_solana_state_certificate_against_commitment(
    certificate_wire: Dict[str, Any],
    sol: SolanaCommitment,
) -> Dict[str, Any]:
    cert = StateCertificate.from_wire_dict(certificate_wire)
    y_live = solana_commitment_to_digest(cert.inner.q, cert.inner.o, sol)
    return _binding_report(cert, y_live, "solana_commitment", sol.to_canonical_dict())


def verify_solana_state_certificate_via_rpc(
    rpc_url: str,
    certificate_wire: Dict[str, Any],
    *,
    cluster_id: str = "mainnet-beta",
    slot: Optional[int] = None,
    commitment: str = "finalized",
    timeout: float = 30.0,
) -> Dict[str, Any]:
    safe_url = validate_public_rpc_url(rpc_url)
    sol = fetch_solana_commitment(
        safe_url,
        cluster_id=cluster_id,
        slot=slot,
        commitment=commitment,
        timeout=timeout,
    )
    return verify_solana_state_certificate_against_commitment(certificate_wire, sol)


def verify_cosmos_state_certificate_against_commitment(
    certificate_wire: Dict[str, Any],
    c: CosmosCommitment,
) -> Dict[str, Any]:
    cert = StateCertificate.from_wire_dict(certificate_wire)
    y_live = cosmos_commitment_to_digest(cert.inner.q, cert.inner.o, c)
    return _binding_report(cert, y_live, "cosmos_commitment", c.to_canonical_dict())


def verify_cosmos_state_certificate_via_rest(
    rest_base: str,
    chain_id: str,
    certificate_wire: Dict[str, Any],
    *,
    height: Optional[int] = None,
    timeout: float = 30.0,
) -> Dict[str, Any]:
    safe_base = validate_public_rpc_url(rest_base)
    c = fetch_cosmos_commitment(
        safe_base,
        chain_id=chain_id,
        height=height,
        timeout=timeout,
    )
    return verify_cosmos_state_certificate_against_commitment(certificate_wire, c)


def verify_xrp_state_certificate_against_commitment(
    certificate_wire: Dict[str, Any],
    x: XrpLedgerCommitment,
) -> Dict[str, Any]:
    cert = StateCertificate.from_wire_dict(certificate_wire)
    y_live = xrp_commitment_to_digest(cert.inner.q, cert.inner.o, x)
    return _binding_report(cert, y_live, "xrp_ledger_commitment", x.to_canonical_dict())


def verify_xrp_state_certificate_via_rpc(
    rpc_url: str,
    certificate_wire: Dict[str, Any],
    *,
    network_id: str,
    ledger_index: LedgerArg = "validated",
    timeout: float = 30.0,
) -> Dict[str, Any]:
    safe_url = validate_public_rpc_url(rpc_url)
    x = fetch_xrp_ledger_commitment(
        safe_url,
        network_id=network_id,
        ledger_index=ledger_index,
        timeout=timeout,
    )
    return verify_xrp_state_certificate_against_commitment(certificate_wire, x)
