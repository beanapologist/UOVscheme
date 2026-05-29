"""Tests for SilentVerify FastAPI SaaS (skipped if fastapi not installed)."""

from __future__ import annotations

import os
import sys

import pytest

pytest.importorskip("fastapi")
from fastapi.testclient import TestClient  # noqa: E402

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

os.environ.setdefault("SILENTVERIFY_UOV_PROFILE", "TOY")
os.environ.setdefault("SILENTVERIFY_API_KEYS", "free:saas-test-key")


@pytest.fixture()
def client(tmp_path, monkeypatch):
    db = tmp_path / "usage.db"
    monkeypatch.setenv("SILENTVERIFY_USAGE_DB", str(db))
    from api.app_common import load_verifier_instance
    from statecert.issuer import load_root_key, load_verifier

    load_root_key.cache_clear()
    load_verifier.cache_clear()
    load_verifier_instance.cache_clear()
    from api import auth

    auth.init_db()
    from api.app import app

    return TestClient(app)


class TestSaasApi:
    def test_health(self, client):
        r = client.get("/api/v1/health")
        assert r.status_code == 200
        assert r.json()["ok"] is True

    def test_chain_catalog(self, client):
        r = client.get("/api/v1/chains")
        assert r.status_code == 200
        ids = {c["id"] for c in r.json()["chains"]}
        assert ids >= {"evm", "solana", "cosmos", "xrp", "evm-cross", "cross-l1"}

    def test_params_includes_chains(self, client):
        r = client.get("/api/v1/params")
        assert "chains" in r.json()

    def test_issue_verify_agent_cert_new_path(self, client):
        r = client.post(
            "/api/v1/certs/agent/issue",
            headers={"X-API-Key": "saas-test-key"},
            json={
                "agent_did": "did:example:agent-1",
                "capabilities": {"deploy": True},
                "expires_in_days": 7,
            },
        )
        assert r.status_code == 200, r.text
        cert = r.json()["cert"]
        v = client.post(
            "/api/v1/certs/agent/verify",
            headers={"X-API-Key": "saas-test-key"},
            json={"cert": cert},
        )
        assert v.json()["valid"] is True

    def test_legacy_agent_paths(self, client):
        r = client.post(
            "/api/v1/issue/agent-cert",
            headers={"X-API-Key": "saas-test-key"},
            json={"agent_did": "did:legacy:1", "capabilities": {}},
        )
        assert r.status_code == 200

    def test_issue_verify_state_cert(self, client):
        r = client.post(
            "/api/v1/certs/state/issue",
            headers={"X-API-Key": "saas-test-key"},
            json={
                "chain_id": "ethereum:1",
                "block_height": 123,
                "state_root_hex": "0xabc",
            },
        )
        assert r.status_code == 200
        cert = r.json()["cert"]
        v = client.post(
            "/api/v1/certs/state/verify",
            headers={"X-API-Key": "saas-test-key"},
            json={"certificate": cert},
        )
        assert v.json()["valid"] is True

    def test_try_page(self, client):
        r = client.get("/docs")
        assert r.status_code == 200
        assert "Use cases" in r.text
        assert "Try SilentVerify" in r.text or "Issue, verify" in r.text

    def test_swagger_page(self, client):
        r = client.get("/swagger")
        assert r.status_code == 200
        assert "swagger-theme.css" in r.text
        assert "Try API" in r.text

    def test_verify_page(self, client):
        r = client.get("/verify")
        assert r.status_code == 200
        assert "Verify certificate" in r.text
        assert "wallet.js" in r.text

    def test_public_verify_no_api_key(self, client):
        issue = client.post(
            "/api/v1/certs/agent/issue",
            headers={"X-API-Key": "saas-test-key"},
            json={"agent_did": "did:public:1", "capabilities": {"read": True}},
        )
        cert = issue.json()["cert"]
        r = client.post("/api/v1/certs/verify", json={"cert": cert})
        assert r.status_code == 200
        assert r.json()["valid"] is True

    def test_public_print_no_api_key(self, client):
        issue = client.post(
            "/api/v1/certs/agent/issue",
            headers={"X-API-Key": "saas-test-key"},
            json={"agent_did": "did:print-pub:1", "capabilities": {}},
        )
        cert = issue.json()["cert"]
        r = client.post("/api/v1/certs/print/public", json={"cert": cert})
        assert r.status_code == 200
        assert "SilentVerify Certificate" in r.text

    def test_print_demo(self, client):
        r = client.get("/api/v1/certs/print/demo")
        assert r.status_code == 200
        assert "SilentVerify Certificate" in r.text
        assert "silentverify-logo.png" in r.text

    def test_print_with_cert(self, client):
        issue = client.post(
            "/api/v1/certs/agent/issue",
            headers={"X-API-Key": "saas-test-key"},
            json={"agent_did": "did:print:1", "capabilities": {}},
        )
        cert = issue.json()["cert"]
        r = client.post(
            "/api/v1/certs/print",
            headers={"X-API-Key": "saas-test-key"},
            json={"cert": cert},
        )
        assert r.status_code == 200
        assert "PASSED" in r.text or "Cryptographic verification" in r.text

    def test_validate_key(self, client):
        bad = client.get(
            "/api/v1/billing/validate-key", headers={"X-API-Key": "not-a-real-key"}
        )
        assert bad.json()["valid"] is False
        good = client.get(
            "/api/v1/billing/validate-key", headers={"X-API-Key": "saas-test-key"}
        )
        assert good.json()["valid"] is True

    def test_missing_api_key(self, client):
        r = client.post(
            "/api/v1/certs/agent/issue",
            json={"agent_did": "did:x", "capabilities": {}},
        )
        assert r.status_code == 401

    def test_agent_wrong_type_on_verify(self, client):
        r = client.post(
            "/api/v1/certs/state/issue",
            headers={"X-API-Key": "saas-test-key"},
            json={
                "chain_id": "solana:mainnet",
                "block_height": 1,
                "state_root_hex": "dead",
            },
        )
        cert = r.json()["cert"]
        v = client.post(
            "/api/v1/certs/agent/verify",
            headers={"X-API-Key": "saas-test-key"},
            json={"cert": cert},
        )
        assert v.json()["valid"] is False

    def test_issue_agent_with_reputation_chain_fields(self, client):
        r = client.post(
            "/api/v1/certs/agent/issue",
            headers={"X-API-Key": "saas-test-key"},
            json={
                "agent_did": "did:example:chained",
                "capabilities": {"sign": True},
                "previousCertDigest": "sha256:0123456789abcdef0123456789abcdef0123456789abcdef0123456789abcdef",
                "taskContext": {"task_id": "deploy-1"},
                "expires_in_days": 7,
            },
        )
        assert r.status_code == 200, r.text
        meta = r.json()["cert"].get("metadata") or {}
        assert meta.get("previous_cert_digest", "").startswith("sha256:")
        assert meta.get("task_context") == {"task_id": "deploy-1"}

    def test_compose_passport_endpoint(self, client):
        agent = client.post(
            "/api/v1/certs/agent/issue",
            headers={"X-API-Key": "saas-test-key"},
            json={
                "agent_did": "did:example:passport",
                "capabilities": {"verify": True},
                "taskContext": {"web_endpoint": "https://agent.example/"},
            },
        )
        assert agent.status_code == 200
        state = client.post(
            "/api/v1/certs/state/issue",
            headers={"X-API-Key": "saas-test-key"},
            json={
                "chain_id": "eip155:1",
                "block_height": 100,
                "state_root_hex": "0x" + "11" * 32,
            },
        )
        assert state.status_code == 200
        r = client.post(
            "/api/v1/certs/compose/passport",
            headers={"X-API-Key": "saas-test-key"},
            json={
                "agentCert": agent.json()["cert"],
                "stateCert": state.json()["cert"],
            },
        )
        assert r.status_code == 200, r.text
        body = r.json()
        assert body["schema"] == "silentverify.erc8004_passport/v1"
        passport = body["passport"]
        assert passport["type"] == "https://eips.ethereum.org/EIPS/eip-8004#registration-v1"
        assert passport["silentverify"]["agent"]["agent_did"] == "did:example:passport"
        assert passport["silentverify"]["state"]["block_height"] == 100


class TestAgentModule:
    def test_agent_digest_deterministic(self):
        from statecert import AgentIdentity, agent_identity_to_digest

        a = AgentIdentity("did:1", {"a": 1}, expires_at_unix=1_700_000_000)
        y1 = agent_identity_to_digest(31, 4, a)
        y2 = agent_identity_to_digest(31, 4, a)
        assert y1 == y2
        assert len(y1) == 4
