"""Cosmos LCD fetcher (mocked)."""

from __future__ import annotations

import json
import os
import sys
from unittest.mock import patch

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from statecert.cosmos_rpc import fetch_cosmos_commitment


class _GetResp:
    def __init__(self, body: dict) -> None:
        self._b = json.dumps(body).encode()

    def read(self) -> bytes:
        return self._b

    def __enter__(self) -> "_GetResp":
        return self

    def __exit__(self, *a: object) -> None:
        return None


def test_fetch_cosmos_commitment_latest():
    body = {
        "block": {
            "header": {
                "height": "18446744",
                "app_hash": "AQIDBA==",  # 0x01020304
            }
        }
    }

    def fake_urlopen(req, timeout=30):  # noqa: ANN001
        assert "blocks/latest" in req.full_url
        return _GetResp(body)

    with patch("statecert.cosmos_rpc.urlopen", side_effect=fake_urlopen):
        c = fetch_cosmos_commitment("https://lcd.example.com", chain_id="cosmoshub-4")

    assert c.chain_id == "cosmoshub-4"
    assert c.height == 18446744
    assert c.app_hash_hex == "0x01020304"
