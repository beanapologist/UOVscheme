"""Compose ERC-8004 agent registration metadata from SilentVerify certificates."""

from __future__ import annotations

from typing import Any, Dict, List, Optional

from statecert import StateCertificate, StateVerifier
from statecert.certificate import certificate_wire_digest

ERC8004_REGISTRATION_TYPE = "https://eips.ethereum.org/EIPS/eip-8004#registration-v1"
DEFAULT_IMAGE = "/static/silentverify-logo.png"


def _did_short_name(agent_did: str) -> str:
    parts = agent_did.strip().split(":")
    return parts[-1] if parts else agent_did


def _chain_summary(meta: Dict[str, Any]) -> Optional[str]:
    chain_id = meta.get("chain_id")
    block_height = meta.get("block_height")
    if chain_id is None and block_height is None:
        anchor = meta.get("anchor")
        if isinstance(anchor, dict):
            chain_id = anchor.get("chain_id")
            block_height = anchor.get("block_height")
    if chain_id is None:
        return None
    if block_height is not None:
        return f"{chain_id} @ block {block_height}"
    return str(chain_id)


def _services_from_context(
    agent_did: str,
    task_context: Optional[Dict[str, Any]],
    verify_base_url: str,
) -> List[Dict[str, Any]]:
    services: List[Dict[str, Any]] = [
        {"name": "DID", "endpoint": agent_did},
        {
            "name": "SilentVerify",
            "endpoint": verify_base_url.rstrip("/") + "/api/v1/certs/verify",
            "version": "v1",
        },
    ]
    if not isinstance(task_context, dict):
        return services

    for key, svc_name in (
        ("mcp_endpoint", "MCP"),
        ("a2a_endpoint", "A2A"),
        ("web_endpoint", "web"),
        ("ens", "ENS"),
    ):
        endpoint = task_context.get(key)
        if isinstance(endpoint, str) and endpoint.strip():
            entry: Dict[str, Any] = {"name": svc_name, "endpoint": endpoint.strip()}
            version = task_context.get(f"{key}_version") or task_context.get(
                f"{svc_name.lower()}_version"
            )
            if isinstance(version, str) and version.strip():
                entry["version"] = version.strip()
            services.append(entry)
    return services


def compose_erc8004_passport(
    *,
    agent_wire: Dict[str, Any],
    state_wire: Dict[str, Any],
    name: Optional[str] = None,
    description: Optional[str] = None,
    image: Optional[str] = None,
    registrations: Optional[List[Dict[str, Any]]] = None,
    verify_base_url: str = "",
) -> Dict[str, Any]:
    """Build clean ERC-8004 registration JSON from agent + state certificates."""
    agent = StateCertificate.from_wire_dict(agent_wire)
    state = StateCertificate.from_wire_dict(state_wire)

    agent_meta = agent.metadata or {}
    state_meta = state.metadata or {}

    if agent_meta.get("cert_type") != "agent":
        raise ValueError("agent_cert must have metadata.cert_type=agent")
    if state_meta.get("cert_type") != "state":
        raise ValueError("state_cert must have metadata.cert_type=state")
    if not StateVerifier.verify_certificate(agent):
        raise ValueError("agent_cert failed cryptographic verification")
    if not StateVerifier.verify_certificate(state):
        raise ValueError("state_cert failed cryptographic verification")

    agent_did = str(agent_meta.get("agent_did") or "unknown-agent")
    chain_line = _chain_summary(state_meta)
    cap_keys = sorted(agent_meta.get("capabilities") or {})
    cap_text = ", ".join(cap_keys) if cap_keys else "general"

    out: Dict[str, Any] = {
        "type": ERC8004_REGISTRATION_TYPE,
        "name": name or _did_short_name(agent_did),
        "description": description
        or (
            f"UOV-backed agent ({agent_did}) with SilentVerify chain state proof"
            + (f" on {chain_line}." if chain_line else ".")
            + f" Capabilities: {cap_text}."
        ),
        "image": image or DEFAULT_IMAGE,
        "active": True,
        "supportedTrust": ["reputation", "crypto-economic"],
        "services": _services_from_context(
            agent_did,
            agent_meta.get("task_context"),
            verify_base_url,
        ),
        "silentverify": {
            "schema": "silentverify.passport/v1",
            "agent": {
                "digest": certificate_wire_digest(agent_wire),
                "pubkey_fp": agent.pubkey_fp,
                "agent_did": agent_did,
                "capabilities": agent_meta.get("capabilities") or {},
                "reputation_hash": agent_meta.get("reputation_hash"),
                "previous_cert_digest": agent_meta.get("previous_cert_digest"),
                "task_context": agent_meta.get("task_context"),
                "expires_at_unix": agent_meta.get("expires_at_unix"),
            },
            "state": {
                "digest": certificate_wire_digest(state_wire),
                "pubkey_fp": state.pubkey_fp,
                "chain_id": state_meta.get("chain_id"),
                "block_height": state_meta.get("block_height"),
                "state_root_hex": state_meta.get("state_root_hex"),
                "anchor": state_meta.get("anchor"),
            },
        },
    }
    if registrations:
        out["registrations"] = registrations
    return out
