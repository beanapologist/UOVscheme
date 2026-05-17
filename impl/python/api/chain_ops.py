"""Fetch live chain anchors, issue certificates, and verify bindings (sync RPC)."""

from __future__ import annotations

from typing import Any, Dict, Optional, Tuple

from statecert import StateCertificate
from statecert.chain_api import (
    fetch_chain_state_evm,
    fetch_cosmos_commitment,
    fetch_solana_commitment,
    fetch_xrp_ledger_commitment,
    validate_public_rpc_url,
    verify_cosmos_state_certificate_via_rest,
    verify_cross_chain_state_transition_via_rpc,
    verify_cross_l1_commitment_via_rpc,
    verify_evm_state_certificate_via_rpc,
    verify_solana_state_certificate_via_rpc,
    verify_xrp_state_certificate_via_rpc,
)
from statecert.chain_api import _fetch_cross_l1_leg  # noqa: PLC2701 — shared leg resolver
from statecert.state_hash import (
    ChainState,
    CrossChainStateTransition,
    CrossL1Commitment,
)

from .app_common import load_verifier_instance, new_rng


def _md(chain: str, extra: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
    base = {"flow": "chain_anchor", "cert_type": "state", "chain": chain}
    if extra:
        base.update(extra)
    return base


# ── Issue (fetch anchor → sign) ─────────────────────────────────────────────


def issue_evm(
    rpc_url: str,
    *,
    block: Any = "latest",
    caip2_chain_id: Optional[str] = None,
    metadata: Optional[Dict[str, Any]] = None,
    timeout: float = 30.0,
    rpc_headers: Optional[Dict[str, str]] = None,
) -> Tuple[StateCertificate, Dict[str, Any]]:
    url = validate_public_rpc_url(rpc_url)
    state = fetch_chain_state_evm(
        url,
        block=block,
        caip2_chain_id=caip2_chain_id,
        timeout=timeout,
        rpc_headers=rpc_headers,
    )
    v = load_verifier_instance()
    cert = v.issue_for_chain_state(
        state, new_rng(), metadata={**_md("evm"), **(metadata or {})}
    )
    return cert, {"chain_state": state.to_canonical_dict()}


def issue_solana(
    rpc_url: str,
    *,
    cluster_id: str = "mainnet-beta",
    slot: Optional[int] = None,
    commitment: str = "finalized",
    metadata: Optional[Dict[str, Any]] = None,
    timeout: float = 30.0,
) -> Tuple[StateCertificate, Dict[str, Any]]:
    url = validate_public_rpc_url(rpc_url)
    sol = fetch_solana_commitment(
        url,
        cluster_id=cluster_id,
        slot=slot,
        commitment=commitment,
        timeout=timeout,
    )
    v = load_verifier_instance()
    cert = v.issue_for_solana(sol, new_rng(), metadata={**_md("solana"), **(metadata or {})})
    return cert, {"solana_commitment": sol.to_canonical_dict()}


def issue_cosmos(
    rest_base: str,
    chain_id: str,
    *,
    height: Optional[int] = None,
    metadata: Optional[Dict[str, Any]] = None,
    timeout: float = 30.0,
) -> Tuple[StateCertificate, Dict[str, Any]]:
    safe = validate_public_rpc_url(rest_base)
    c = fetch_cosmos_commitment(
        safe, chain_id=chain_id.strip(), height=height, timeout=timeout
    )
    v = load_verifier_instance()
    cert = v.issue_for_cosmos(c, new_rng(), metadata={**_md("cosmos"), **(metadata or {})})
    return cert, {"cosmos_commitment": c.to_canonical_dict()}


def issue_xrp(
    rpc_url: str,
    *,
    network_id: str,
    ledger_index: Any = "validated",
    metadata: Optional[Dict[str, Any]] = None,
    timeout: float = 30.0,
) -> Tuple[StateCertificate, Dict[str, Any]]:
    url = validate_public_rpc_url(rpc_url)
    x = fetch_xrp_ledger_commitment(
        url,
        network_id=network_id.strip(),
        ledger_index=ledger_index,
        timeout=timeout,
    )
    v = load_verifier_instance()
    cert = v.issue_for_xrp(x, new_rng(), metadata={**_md("xrp"), **(metadata or {})})
    return cert, {"xrp_ledger_commitment": x.to_canonical_dict()}


def issue_evm_cross(
    src: Dict[str, Any],
    dst: Dict[str, Any],
    *,
    metadata: Optional[Dict[str, Any]] = None,
    timeout: float = 30.0,
) -> Tuple[StateCertificate, Dict[str, Any]]:
    s_url = validate_public_rpc_url(str(src["rpc_url"]).strip())
    d_url = validate_public_rpc_url(str(dst["rpc_url"]).strip())
    s_block = src.get("block", "latest")
    d_block = dst.get("block", "latest")
    s_caip = src.get("caip2_chain_id")
    d_caip = dst.get("caip2_chain_id")
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
    x = CrossChainStateTransition(src=src_state, dst=dst_state)
    v = load_verifier_instance()
    cert = v.issue_for_cross_chain(
        x, new_rng(), metadata={**_md("evm_cross"), **(metadata or {})}
    )
    return cert, {"cross_chain_state_transition": x.to_canonical_dict()}


def issue_cross_l1(
    src: Dict[str, Any],
    dst: Dict[str, Any],
    *,
    metadata: Optional[Dict[str, Any]] = None,
    timeout: float = 30.0,
) -> Tuple[StateCertificate, Dict[str, Any]]:
    src_a = _fetch_cross_l1_leg(src, side="src", policy_leg=None, timeout=timeout)
    dst_a = _fetch_cross_l1_leg(dst, side="dst", policy_leg=None, timeout=timeout)
    x = CrossL1Commitment(src=src_a, dst=dst_a)
    v = load_verifier_instance()
    cert = v.issue_for_cross_l1(
        x, new_rng(), metadata={**_md("cross_l1"), **(metadata or {})}
    )
    return cert, {"cross_l1_commitment": x.to_canonical_dict()}


# ── Verify (re-export for typing) ───────────────────────────────────────────

verify_evm = verify_evm_state_certificate_via_rpc
verify_solana = verify_solana_state_certificate_via_rpc
verify_cosmos = verify_cosmos_state_certificate_via_rest
verify_xrp = verify_xrp_state_certificate_via_rpc
verify_evm_cross = verify_cross_chain_state_transition_via_rpc
verify_cross_l1 = verify_cross_l1_commitment_via_rpc
