"""Committed Foundry fixture stays consistent with Python verification."""

from __future__ import annotations

import json
import os
import sys
from pathlib import Path

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from statecert import StateCertificate, StateVerifier

REPO_ROOT = Path(__file__).resolve().parents[3]
WIRE = REPO_ROOT / "contracts" / "test" / "fixtures" / "state_cert_wire.json"
PKBIN = REPO_ROOT / "contracts" / "test" / "fixtures" / "pubkey_fp.bin"


def test_foundry_fixture_wire_verifies_in_python():
    assert WIRE.is_file(), "run: python3 impl/python/scripts/gen_foundry_fixture.py"
    raw = WIRE.read_text(encoding="utf-8")
    cert = StateCertificate.from_json(raw)
    assert StateVerifier.verify_certificate(cert)
    assert cert.pubkey_fp == PKBIN.read_bytes().hex()


def test_foundry_fixture_wire_is_silentverify_schema():
    d = json.loads(WIRE.read_text(encoding="utf-8"))
    assert d.get("schema_version") == "silentverify.state_cert/v1"
    assert d.get("q") == 251 and d.get("o") == 8 and d.get("v") == 24
