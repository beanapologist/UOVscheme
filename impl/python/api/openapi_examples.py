"""Realistic OpenAPI examples (generated once from toy UOV params)."""

from __future__ import annotations

import os
import random
import warnings
from functools import lru_cache
from typing import Any, Dict


@lru_cache(maxsize=1)
def sample_agent_cert_wire() -> Dict[str, Any]:
    """Valid agent cert wire dict for Swagger «Example Value»."""
    os.environ.setdefault("SILENTVERIFY_UOV_PROFILE", "TOY")
    from statecert import agent_identity_from_request
    from statecert.issuer import load_root_key, load_verifier

    load_root_key.cache_clear()
    load_verifier.cache_clear()
    from uov import RandomAdapter

    with warnings.catch_warnings():
        warnings.simplefilter("ignore", UserWarning)
        v = load_verifier()
        identity = agent_identity_from_request(
            agent_did="did:example:acme-agent-7",
            capabilities={"sign": True, "deploy": True},
            expires_in_days=30,
        )
        cert = v.issue_for_agent(identity, RandomAdapter(random.Random(0)))
    return cert.to_wire_dict()


@lru_cache(maxsize=1)
def sample_state_cert_wire() -> Dict[str, Any]:
    """Valid state-anchor cert for Swagger verify examples."""
    os.environ.setdefault("SILENTVERIFY_UOV_PROFILE", "TOY")
    from statecert import ChainState
    from statecert.issuer import load_root_key, load_verifier

    load_root_key.cache_clear()
    load_verifier.cache_clear()
    from uov import RandomAdapter

    with warnings.catch_warnings():
        warnings.simplefilter("ignore", UserWarning)
        v = load_verifier()
        state = ChainState("eip155:1", 19_000_000, "0x" + "ab" * 32)
        cert = v.issue_for_chain_state(
            state,
            RandomAdapter(random.Random(1)),
            metadata={"cert_type": "state", "flow": "state_anchor"},
        )
    return cert.to_wire_dict()


@lru_cache(maxsize=1)
def sample_issue_response() -> Dict[str, Any]:
    wire = sample_agent_cert_wire()
    return {
        "status": "issued",
        "cert": wire,
        "pubkey_fp": wire["pubkey_fp"],
    }


@lru_cache(maxsize=1)
def sample_chain_issue_response() -> Dict[str, Any]:
    wire = sample_agent_cert_wire()
    return {
        "status": "issued",
        "cert": wire,
        "pubkey_fp": wire["pubkey_fp"],
        "anchor": {
            "kind": "ChainState",
            "chain_id": "eip155:1",
            "block_height": 19000000,
            "state_root_hex": "0x" + "ab" * 32,
        },
    }


SAMPLE_VERIFY_OK: Dict[str, Any] = {
    "valid": True,
    "pubkey_fp": "7f3a9c2e1b0456d8a0f1e2d3c4b5a6978e9f0a1b2c3d4e5f6a7b8c9d0e1f2a3",
    "cert_type": "agent",
    "detail": None,
}

SAMPLE_VERIFY_FAIL: Dict[str, Any] = {
    "valid": False,
    "pubkey_fp": "7f3a9c2e1b0456d8a0f1e2d3c4b5a6978e9f0a1b2c3d4e5f6a7b8c9d0e1f2a3",
    "cert_type": "agent",
    "detail": "signature_or_fingerprint_failed",
}

SAMPLE_CHAIN_VERIFY: Dict[str, Any] = {
    "result": {
        "ok": True,
        "digest_binds_to_anchor": True,
        "certificate_crypto_ok": True,
        "certificate_full_ok": True,
        "computed_digest_y": [12, 5, 28, 19],
        "chain_state": {
            "kind": "ChainState",
            "chain_id": "eip155:1",
            "block_height": 19000000,
            "state_root_hex": "0x" + "ab" * 32,
        },
    }
}
