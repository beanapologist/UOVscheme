"""Solana JSON-RPC fetcher (mocked)."""

from __future__ import annotations

import json
import os
import sys
from unittest.mock import patch

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from statecert.solana_rpc import fetch_solana_commitment


class _Resp:
    def __init__(self, d: dict) -> None:
        self._b = json.dumps(d).encode()

    def read(self) -> bytes:
        return self._b

    def __enter__(self) -> "_Resp":
        return self

    def __exit__(self, *a: object) -> None:
        return None


def test_fetch_solana_commitment_fixed_slot():
    calls: list[dict] = []

    def fake_urlopen(req, timeout=30):  # noqa: ANN001
        data = json.loads(req.data.decode())
        calls.append(data)
        if data["method"] == "getBlock":
            return _Resp(
                {
                    "jsonrpc": "2.0",
                    "id": 1,
                    "result": {
                        "blockhash": "8dFhP9xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx"
                    },
                }
            )
        raise AssertionError(data["method"])

    with patch("statecert.jsonrpc.urlopen", side_effect=fake_urlopen):
        c = fetch_solana_commitment(
            "https://api.devnet.solana.com", cluster_id="devnet", slot=12345
        )

    assert len(calls) == 1
    assert c.cluster_id == "devnet"
    assert c.slot == 12345
    assert c.blockhash_b58.startswith("8dFh")


def test_fetch_solana_head_uses_get_slot_then_block():
    seq = iter(
        [
            _Resp({"jsonrpc": "2.0", "id": 1, "result": 42}),
            _Resp(
                {
                    "jsonrpc": "2.0",
                    "id": 1,
                    "result": {
                        "blockhash": "AbCdEfGhIjKlMnOpQrStUvWxYz1234567890abcde"
                    },
                }
            ),
        ]
    )

    def fake_urlopen(req, timeout=30):  # noqa: ANN001
        return next(seq)

    with patch("statecert.jsonrpc.urlopen", side_effect=fake_urlopen):
        c = fetch_solana_commitment("https://x", cluster_id="mainnet-beta")

    assert c.slot == 42
