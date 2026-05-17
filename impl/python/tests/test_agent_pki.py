"""Agent PKI helpers (statecert.agent + StateVerifier.issue_for_agent)."""

from __future__ import annotations

import random

import pytest

from uov import RandomAdapter, keygen
from statecert import AgentIdentity, StateVerifier
from statecert.agent import agent_identity_from_request, agent_identity_to_digest


def _toy_key():
    return keygen(31, 4, 8, rng=RandomAdapter(random.Random(1)), allow_toy_params=True)


class TestAgentPKI:
    def test_identity_from_request_expiry(self):
        ident = agent_identity_from_request(
            agent_did="did:example:agent",
            capabilities={"deploy": True},
            reputation_hash="rep",
            anchor={"chain_id": "eip155:1"},
            expires_in_days=14,
        )
        assert ident.expires_at_unix is not None
        d = ident.to_canonical_dict()
        assert d["agent_did"] == "did:example:agent"
        assert d["reputation_hash"] == "rep"
        assert d["anchor"]["chain_id"] == "eip155:1"

    def test_identity_validation(self):
        with pytest.raises(ValueError, match="agent_did"):
            AgentIdentity("", {}).to_canonical_dict()
        with pytest.raises(ValueError, match="capabilities"):
            AgentIdentity("did:x", "not-a-dict").to_canonical_dict()  # type: ignore[arg-type]
        with pytest.raises(ValueError, match="expires_in_days"):
            agent_identity_from_request(
                agent_did="did:x", capabilities={}, expires_in_days=0
            )

    def test_issue_for_agent_roundtrip(self):
        k = _toy_key()
        v = StateVerifier(k)
        ident = agent_identity_from_request(
            agent_did="did:example:acme",
            capabilities={"sign": True},
            expires_in_days=30,
        )
        cert = v.issue_for_agent(ident, RandomAdapter(random.Random(2)))
        assert StateVerifier.verify_certificate(cert)
        meta = cert.to_wire_dict().get("metadata") or {}
        assert meta.get("cert_type") == "agent"
        assert meta.get("agent_did") == "did:example:acme"

    def test_digest_stable(self):
        a = AgentIdentity("did:1", {"k": 1}, expires_at_unix=1_800_000_000)
        y1 = agent_identity_to_digest(31, 4, a)
        y2 = agent_identity_to_digest(31, 4, a)
        assert y1 == y2
