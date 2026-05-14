"""Server-side helpers: validate public HTTP(S) URLs, fetch live anchors, bind state certificates."""

from __future__ import annotations

import ipaddress
import os
from typing import Any, Dict, List, Optional

from .certificate import StateCertificate
from .cosmos_rpc import fetch_cosmos_commitment
from .evm_rpc import BlockArg, fetch_chain_state_evm
from .solana_rpc import fetch_solana_commitment
from .state_hash import (
    ChainState,
    CosmosCommitment,
    SolanaCommitment,
    XrpLedgerCommitment,
    chain_state_to_digest,
    cosmos_commitment_to_digest,
    solana_commitment_to_digest,
    xrp_commitment_to_digest,
)
from .xrp_rpc import LedgerArg, fetch_xrp_ledger_commitment


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


def verify_evm_state_certificate_via_rpc(
    rpc_url: str,
    block: BlockArg,
    certificate_wire: Dict[str, Any],
    *,
    caip2_chain_id: Optional[str] = None,
    timeout: float = 30.0,
) -> Dict[str, Any]:
    safe_url = validate_public_rpc_url(rpc_url)
    state = fetch_chain_state_evm(
        safe_url,
        block=block,
        caip2_chain_id=caip2_chain_id,
        timeout=timeout,
    )
    return verify_evm_state_certificate_against_chain(certificate_wire, state)


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
