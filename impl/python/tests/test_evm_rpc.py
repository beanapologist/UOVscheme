"""Tests for JSON-RPC helpers (mocked HTTP; no live network)."""

from __future__ import annotations

import json
import os
import sys
from unittest.mock import MagicMock, patch

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from statecert.evm_rpc import fetch_chain_state_evm


class _FakeResp:
    def __init__(self, payload: dict) -> None:
        self._raw = json.dumps(payload).encode()

    def read(self) -> bytes:
        return self._raw

    def __enter__(self) -> "_FakeResp":
        return self

    def __exit__(self, *args: object) -> None:
        return None


def test_fetch_chain_state_evm_roundtrip():
    calls: list[dict] = []

    def fake_urlopen(req, timeout=30):  # noqa: ANN001
        data = json.loads(req.data.decode())
        calls.append(data)
        if data["method"] == "eth_chainId":
            return _FakeResp({"jsonrpc": "2.0", "id": 1, "result": "0xaa36a7"})
        if data["method"] == "eth_getBlockByNumber":
            return _FakeResp(
                {
                    "jsonrpc": "2.0",
                    "id": 1,
                    "result": {
                        "number": "0x10",
                        "stateRoot": "0x" + "cd" * 32,
                    },
                }
            )
        raise AssertionError(f"unexpected method {data['method']}")

    with patch("statecert.jsonrpc.urlopen", side_effect=fake_urlopen):
        cs = fetch_chain_state_evm("https://example.invalid/v1")

    assert [c["method"] for c in calls] == ["eth_chainId", "eth_getBlockByNumber"]
    assert cs.chain_id == "eip155:11155111"
    assert cs.block_height == 16
    assert cs.state_root_hex == "0x" + "cd" * 32


def test_fetch_with_explicit_caip2_skips_chain_id():
    calls: list[dict] = []

    def fake_urlopen(req, timeout=30):  # noqa: ANN001
        data = json.loads(req.data.decode())
        calls.append(data)
        assert data["method"] == "eth_getBlockByNumber"
        return _FakeResp(
            {
                "jsonrpc": "2.0",
                "id": 1,
                "result": {"number": "0x1", "stateRoot": "0x" + "11" * 32},
            }
        )

    with patch("statecert.jsonrpc.urlopen", side_effect=fake_urlopen):
        cs = fetch_chain_state_evm(
            "https://example.invalid",
            block=1,
            caip2_chain_id="eip155:1",
        )

    assert len(calls) == 1
    assert cs.chain_id == "eip155:1"
    assert cs.block_height == 1


def test_rpc_error_raises():
    def fake_urlopen(req, timeout=30):  # noqa: ANN001
        return _FakeResp({"jsonrpc": "2.0", "id": 1, "error": {"code": -32000, "message": "oops"}})

    with patch("statecert.jsonrpc.urlopen", side_effect=fake_urlopen):
        try:
            fetch_chain_state_evm("https://x", caip2_chain_id="eip155:1", block="latest")
        except RuntimeError as e:
            assert "RPC error" in str(e)
        else:
            raise AssertionError("expected RuntimeError")
