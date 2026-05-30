"""Tests for ERC-8004 passport composition."""

from __future__ import annotations

import random

import pytest

from uov import RandomAdapter, keygen
from statecert import ChainState, StateVerifier, agent_identity_from_request
from statecert.certificate import certificate_wire_digest
from api.passport import ERC8004_REGISTRATION_TYPE, compose_erc8004_passport


def _toy_key():
    return keygen(31, 4, 8, rng=RandomAdapter(random.Random(1)), allow_toy_params=True)


class TestPassportCompose:
    def test_certificate_wire_digest_stable(self):
        k = _toy_key()
        v = StateVerifier(k)
        ident = agent_identity_from_request(
            agent_did="did:example:a",
            capabilities={"sign": True},
            expires_in_days=7,
        )
        wire = v.issue_for_agent(ident, RandomAdapter(random.Random(2))).to_wire_dict()
        d1 = certificate_wire_digest(wire)
        d2 = certificate_wire_digest(wire)
        assert d1 == d2
        assert d1.startswith("sha256:")

    def test_compose_passport_happy_path(self):
        k = _toy_key()
        v = StateVerifier(k)
        ident = agent_identity_from_request(
            agent_did="did:example:passport-agent",
            capabilities={"deploy": True},
            previous_cert_digest="sha256:deadbeef",
            task_context={"task_id": "job-1", "mcp_endpoint": "https://mcp.test/"},
            expires_in_days=30,
        )
        agent_wire = v.issue_for_agent(
            ident, RandomAdapter(random.Random(3))
        ).to_wire_dict()
        state = ChainState("eip155:1", 42, "0x" + "cd" * 32)
        state_wire = v.issue_for_chain_state(
            state,
            RandomAdapter(random.Random(4)),
            metadata={
                "cert_type": "state",
                "flow": "state_anchor",
                "chain_id": "eip155:1",
                "block_height": 42,
                "state_root_hex": "0x" + "cd" * 32,
            },
        ).to_wire_dict()

        passport = compose_erc8004_passport(
            agent_wire=agent_wire,
            state_wire=state_wire,
            verify_base_url="https://api.example.com",
        )
        assert passport["type"] == ERC8004_REGISTRATION_TYPE
        assert passport["name"] == "passport-agent"
        assert "services" in passport
        assert (
            passport["silentverify"]["agent"]["previous_cert_digest"]
            == "sha256:deadbeef"
        )
        assert passport["silentverify"]["state"]["chain_id"] == "eip155:1"
        mcp = [s for s in passport["services"] if s.get("name") == "MCP"]
        assert mcp and mcp[0]["endpoint"] == "https://mcp.test/"

    def test_compose_rejects_wrong_cert_type(self):
        k = _toy_key()
        v = StateVerifier(k)
        ident = agent_identity_from_request(
            agent_did="did:example:x", capabilities={}, expires_in_days=7
        )
        agent_wire = v.issue_for_agent(
            ident, RandomAdapter(random.Random(5))
        ).to_wire_dict()
        with pytest.raises(ValueError, match="state_cert"):
            compose_erc8004_passport(agent_wire=agent_wire, state_wire=agent_wire)
