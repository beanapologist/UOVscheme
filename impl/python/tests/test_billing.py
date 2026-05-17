"""Billing and free API key tests."""

from __future__ import annotations

import os
import sys

import pytest

pytest.importorskip("fastapi")
from fastapi.testclient import TestClient  # noqa: E402

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

os.environ.setdefault("SILENTVERIFY_UOV_PROFILE", "TOY")


@pytest.fixture()
def client(tmp_path, monkeypatch):
    monkeypatch.setenv("SILENTVERIFY_USAGE_DB", str(tmp_path / "usage.db"))
    monkeypatch.setenv("SILENTVERIFY_API_KEYS", "")
    from api.app_common import load_verifier_instance
    from statecert.issuer import load_root_key, load_verifier

    load_root_key.cache_clear()
    load_verifier.cache_clear()
    load_verifier_instance.cache_clear()
    from api import auth

    auth.init_db()
    from api.app import app

    return TestClient(app)


def test_billing_status(client):
    r = client.get("/api/v1/billing/status")
    assert r.status_code == 200
    assert "plans" in r.json()


def test_free_key_issue_and_use(client):
    r = client.post("/api/v1/billing/free-key")
    assert r.status_code == 200
    key = r.json()["api_key"]
    assert key.startswith("sv_free_")
    issue = client.post(
        "/api/v1/certs/agent/issue",
        headers={"X-API-Key": key},
        json={"agent_did": "did:example:acme-1", "capabilities": {"read": True}},
    )
    assert issue.status_code == 200, issue.text


def test_landing_page(client):
    r = client.get("/")
    assert r.status_code == 200
    assert "SilentVerify" in r.text
    assert "COINjecture Network LLC" in r.text
