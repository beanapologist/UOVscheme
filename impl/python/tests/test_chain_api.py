"""Tests for :mod:`statecert.chain_api` (RPC URL policy + digest binding)."""

from __future__ import annotations

import os
import random
import sys
import warnings

import pytest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from statecert import (
    ChainState,
    CosmosCommitment,
    SolanaCommitment,
    StateVerifier,
)
import statecert.chain_api as chain_api_mod
import statecert.xrp_rpc as xrp_rpc_mod

from statecert.chain_api import (
    enforce_evm_min_confirmations_behind_tip,
    validate_public_rpc_url,
    verify_cosmos_state_certificate_against_commitment,
    verify_cosmos_state_certificate_via_rest,
    verify_cross_chain_state_transition_against_pair,
    verify_cross_chain_state_transition_via_rpc,
    verify_cross_l1_commitment_against_pair,
    verify_cross_l1_commitment_via_rpc,
    verify_evm_state_certificate_against_chain,
    verify_evm_state_certificate_via_rpc,
    verify_solana_state_certificate_against_commitment,
    verify_solana_state_certificate_via_rpc,
    verify_xrp_state_certificate_against_commitment,
    verify_xrp_state_certificate_via_rpc,
)
from statecert.state_hash import CrossChainStateTransition, CrossL1Commitment, XrpLedgerCommitment
from uov import RandomAdapter, keygen


def _rng(seed: int = 0) -> RandomAdapter:
    return RandomAdapter(random.Random(seed))


def _toy_key(seed: int = 1):
    with warnings.catch_warnings():
        warnings.simplefilter("ignore", UserWarning)
        return keygen(31, 4, 8, rng=_rng(seed), allow_toy_params=True)


class TestValidatePublicRpcUrl:
    def test_https_public_ok(self):
        validate_public_rpc_url("https://ethereum.publicnode.com")

    def test_localhost_blocked_by_default(self, monkeypatch):
        monkeypatch.delenv("SILENTVERIFY_ALLOW_LOOPBACK_RPC", raising=False)
        with pytest.raises(ValueError, match="localhost"):
            validate_public_rpc_url("http://localhost:8545")

    def test_loopback_ip_blocked_by_default(self, monkeypatch):
        monkeypatch.delenv("SILENTVERIFY_ALLOW_LOOPBACK_RPC", raising=False)
        with pytest.raises(ValueError, match="non-public"):
            validate_public_rpc_url("http://127.0.0.1:8545")

    def test_loopback_allowed_with_env(self, monkeypatch):
        monkeypatch.setenv("SILENTVERIFY_ALLOW_LOOPBACK_RPC", "1")
        validate_public_rpc_url("http://127.0.0.1:8545")
        validate_public_rpc_url("http://localhost:8545")

    def test_bad_scheme(self):
        with pytest.raises(ValueError, match="http"):
            validate_public_rpc_url("ftp://example.com")

    def test_missing_host(self):
        with pytest.raises(ValueError, match="host"):
            validate_public_rpc_url("https:///")


class TestVerifyEvmCertAgainstChain:
    def test_binding_ok_when_state_matches(self):
        k = _toy_key()
        v = StateVerifier(k)
        cs = ChainState("eip155:11155111", 5_000_000, "0xabc123")
        cert = v.issue_for_chain_state(cs, _rng(9))
        wire = cert.to_wire_dict()
        out = verify_evm_state_certificate_against_chain(wire, cs)
        assert out["digest_binds_to_anchor"] is True
        assert out["certificate_crypto_ok"] is True
        assert out["certificate_full_ok"] is True
        assert out["ok"] is True

    def test_binding_fails_when_state_differs(self):
        k = _toy_key()
        v = StateVerifier(k)
        cs = ChainState("eip155:11155111", 5_000_000, "0xabc123")
        cert = v.issue_for_chain_state(cs, _rng(9))
        wire = cert.to_wire_dict()
        other = ChainState("eip155:11155111", 5_000_001, "0xabc123")
        out = verify_evm_state_certificate_against_chain(wire, other)
        assert out["digest_binds_to_anchor"] is False
        assert out["ok"] is False

    def test_via_rpc_uses_fetch_mock(self, monkeypatch):
        k = _toy_key()
        v = StateVerifier(k)
        cs = ChainState("eip155:1", 12_345, "0xdead")
        cert = v.issue_for_chain_state(cs, _rng(11))
        wire = cert.to_wire_dict()

        def fake_fetch(
            url: str,
            *,
            block,
            caip2_chain_id=None,
            timeout: float = 30.0,
        ):
            assert "example.com" in url
            assert block == "latest"
            assert caip2_chain_id == "eip155:1"
            return cs

        monkeypatch.setattr(chain_api_mod, "fetch_chain_state_evm", fake_fetch)
        out = verify_evm_state_certificate_via_rpc(
            "https://rpc.example.com/v1",
            "latest",
            wire,
            caip2_chain_id="eip155:1",
        )
        assert out["ok"] is True
        assert out["digest_binds_to_anchor"] is True


class TestCrossChainEvmTransition:
    def test_pair_binding_ok(self):
        k = _toy_key()
        v = StateVerifier(k)
        src = ChainState("eip155:1", 1, "0x" + "aa" * 32)
        dst = ChainState("eip155:42161", 2, "0x" + "bb" * 32)
        x = CrossChainStateTransition(src=src, dst=dst)
        cert = v.issue_for_cross_chain(x, _rng(12))
        wire = cert.to_wire_dict()
        out = verify_cross_chain_state_transition_against_pair(wire, src, dst)
        assert out["ok"] is True
        assert out["digest_binds_to_anchor"] is True
        assert "cross_chain_state_transition" in out

    def test_pair_binding_fails_if_dst_wrong(self):
        k = _toy_key()
        v = StateVerifier(k)
        src = ChainState("eip155:1", 1, "0x" + "aa" * 32)
        dst = ChainState("eip155:42161", 2, "0x" + "bb" * 32)
        cert = v.issue_for_cross_chain(
            CrossChainStateTransition(src=src, dst=dst), _rng(13)
        )
        wire = cert.to_wire_dict()
        bad_dst = ChainState("eip155:42161", 3, "0x" + "bb" * 32)
        out = verify_cross_chain_state_transition_against_pair(wire, src, bad_dst)
        assert out["digest_binds_to_anchor"] is False
        assert out["ok"] is False

    def test_via_rpc_dual_fetch_mock(self, monkeypatch):
        k = _toy_key()
        v = StateVerifier(k)
        src = ChainState("eip155:1", 10, "0x" + "cc" * 32)
        dst = ChainState("eip155:10", 20, "0x" + "dd" * 32)
        cert = v.issue_for_cross_chain(
            CrossChainStateTransition(src=src, dst=dst), _rng(14)
        )
        wire = cert.to_wire_dict()
        calls = []

        def fake_fetch(url, *, block, caip2_chain_id=None, timeout: float = 30.0):
            calls.append((url, block, caip2_chain_id))
            if "eth-a" in url:
                assert block == "finalized"
                assert caip2_chain_id == "eip155:1"
                return src
            if "eth-b" in url:
                assert block == 20
                return dst
            raise AssertionError(url)

        monkeypatch.setattr(chain_api_mod, "fetch_chain_state_evm", fake_fetch)
        out = verify_cross_chain_state_transition_via_rpc(
            wire,
            src={"rpc_url": "https://eth-a.example", "block": "finalized", "caip2_chain_id": "eip155:1"},
            dst={"rpc_url": "https://eth-b.example", "block": 20},
        )
        assert len(calls) == 2
        assert out["ok"] is True


class TestCrossL1Commitment:
    def test_evm_solana_binding_ok(self):
        k = _toy_key()
        v = StateVerifier(k)
        ev = ChainState("eip155:1", 1, "0x" + "11" * 32)
        sol = SolanaCommitment("mainnet-beta", 99, "Ab58Hash")
        x = CrossL1Commitment(src=ev, dst=sol)
        cert = v.issue_for_cross_l1(x, _rng(20))
        wire = cert.to_wire_dict()
        out = verify_cross_l1_commitment_against_pair(wire, ev, sol)
        assert out["ok"] is True
        assert out["digest_binds_to_anchor"] is True
        assert "cross_l1_commitment" in out

    def test_evm_solana_wrong_dst_fails(self):
        k = _toy_key()
        v = StateVerifier(k)
        ev = ChainState("eip155:1", 1, "0x" + "11" * 32)
        sol = SolanaCommitment("mainnet-beta", 99, "Ab58Hash")
        cert = v.issue_for_cross_l1(CrossL1Commitment(src=ev, dst=sol), _rng(21))
        wire = cert.to_wire_dict()
        bad_sol = SolanaCommitment("mainnet-beta", 100, "Ab58Hash")
        out = verify_cross_l1_commitment_against_pair(wire, ev, bad_sol)
        assert out["ok"] is False
        assert out["digest_binds_to_anchor"] is False

    def test_via_rpc_dual_leg_mock(self, monkeypatch):
        k = _toy_key()
        v = StateVerifier(k)
        ev = ChainState("eip155:1", 5, "0x" + "22" * 32)
        sol = SolanaCommitment("devnet", 12, "bh58")
        cert = v.issue_for_cross_l1(CrossL1Commitment(src=ev, dst=sol), _rng(22))
        wire = cert.to_wire_dict()
        calls: list = []

        def fake_evm(url, *, block, caip2_chain_id=None, timeout: float = 30.0):
            calls.append(("evm", url, block))
            assert "eth-l1" in url
            return ev

        def fake_sol(
            url,
            *,
            cluster_id: str = "mainnet-beta",
            slot=None,
            commitment: str = "finalized",
            timeout: float = 30.0,
        ):
            calls.append(("sol", url, cluster_id))
            assert "solana-l1" in url
            return sol

        monkeypatch.setattr(chain_api_mod, "fetch_chain_state_evm", fake_evm)
        monkeypatch.setattr(chain_api_mod, "fetch_solana_commitment", fake_sol)
        out = verify_cross_l1_commitment_via_rpc(
            wire,
            src={
                "kind": "evm",
                "rpc_url": "https://eth-l1.example",
                "block": "finalized",
                "caip2_chain_id": "eip155:1",
            },
            dst={
                "kind": "solana",
                "rpc_url": "https://solana-l1.example",
                "cluster_id": "devnet",
            },
        )
        assert len(calls) == 2
        assert out["ok"] is True


class TestEvmDepthPolicy:
    def test_enforce_depth_passes(self, monkeypatch):
        src = ChainState("eip155:1", 100, "0x" + "ee" * 32)

        def fake_jsonrpc(url, method, params, *, timeout: float = 30.0):
            assert method == "eth_blockNumber"
            return "0x6a"  # 106 → depth 6

        monkeypatch.setattr(chain_api_mod, "jsonrpc_call", fake_jsonrpc)
        enforce_evm_min_confirmations_behind_tip(
            "https://rpc.example.com", src, 5, timeout=1.0
        )

    def test_enforce_depth_fails(self, monkeypatch):
        src = ChainState("eip155:1", 104, "0x" + "ee" * 32)

        def fake_jsonrpc(url, method, params, *, timeout: float = 30.0):
            return "0x6a"  # 106 → depth 2

        monkeypatch.setattr(chain_api_mod, "jsonrpc_call", fake_jsonrpc)
        with pytest.raises(ValueError, match="evm policy"):
            enforce_evm_min_confirmations_behind_tip(
                "https://rpc.example.com", src, 5, timeout=1.0
            )

    def test_via_rpc_applies_policy(self, monkeypatch):
        k = _toy_key()
        v = StateVerifier(k)
        cs = ChainState("eip155:1", 1000, "0x" + "fa" * 32)
        cert = v.issue_for_chain_state(cs, _rng(15))
        wire = cert.to_wire_dict()

        def fake_fetch(url, *, block, caip2_chain_id=None, timeout: float = 30.0):
            return cs

        def fake_jsonrpc(url, method, params, *, timeout: float = 30.0):
            return "0x3f7"  # 1015 → depth 15

        monkeypatch.setattr(chain_api_mod, "fetch_chain_state_evm", fake_fetch)
        monkeypatch.setattr(chain_api_mod, "jsonrpc_call", fake_jsonrpc)
        out = verify_evm_state_certificate_via_rpc(
            "https://rpc.example.com",
            "latest",
            wire,
            caip2_chain_id="eip155:1",
            policy={"min_confirmations_behind_tip": 10},
        )
        assert out["ok"] is True


class TestSolanaCosmosXrpBinding:
    def test_solana_match(self):
        k = _toy_key()
        v = StateVerifier(k)
        s = SolanaCommitment("mainnet-beta", 300_000_000, "SomeBlockHashB58")
        cert = v.issue_for_solana(s, _rng(3))
        wire = cert.to_wire_dict()
        out = verify_solana_state_certificate_against_commitment(wire, s)
        assert out["ok"] is True
        assert out["digest_binds_to_anchor"] is True

    def test_cosmos_match(self):
        k = _toy_key()
        v = StateVerifier(k)
        c = CosmosCommitment("cosmoshub-4", 18_000_000, "0x" + "cd" * 32)
        cert = v.issue_for_cosmos(c, _rng(4))
        wire = cert.to_wire_dict()
        out = verify_cosmos_state_certificate_against_commitment(wire, c)
        assert out["ok"] is True

    def test_xrp_match(self):
        k = _toy_key()
        v = StateVerifier(k)
        x = XrpLedgerCommitment("xrpl-mainnet", 99_000_000, "0x" + "ef" * 32)
        cert = v.issue_for_anchor(x, _rng(5))
        wire = cert.to_wire_dict()
        out = verify_xrp_state_certificate_against_commitment(wire, x)
        assert out["ok"] is True

    def test_solana_via_rpc_mock(self, monkeypatch):
        k = _toy_key()
        v = StateVerifier(k)
        s = SolanaCommitment("devnet", 12, "bh58")
        cert = v.issue_for_solana(s, _rng(6))
        wire = cert.to_wire_dict()

        def fake_fetch(
            url: str,
            *,
            cluster_id: str = "mainnet-beta",
            slot=None,
            commitment: str = "finalized",
            timeout: float = 30.0,
        ):
            assert "solana.example" in url
            assert cluster_id == "devnet"
            return s

        monkeypatch.setattr(chain_api_mod, "fetch_solana_commitment", fake_fetch)
        out = verify_solana_state_certificate_via_rpc(
            "https://api.solana.example",
            wire,
            cluster_id="devnet",
        )
        assert out["ok"] is True

    def test_cosmos_via_rest_mock(self, monkeypatch):
        k = _toy_key()
        v = StateVerifier(k)
        c = CosmosCommitment("test-1", 44, "0x" + "11" * 32)
        cert = v.issue_for_cosmos(c, _rng(7))
        wire = cert.to_wire_dict()

        def fake_fetch(
            rest_base: str,
            *,
            chain_id: str,
            height=None,
            timeout: float = 30.0,
        ):
            assert "lcd.example" in rest_base
            assert chain_id == "test-1"
            return c

        monkeypatch.setattr(chain_api_mod, "fetch_cosmos_commitment", fake_fetch)
        out = verify_cosmos_state_certificate_via_rest(
            "https://lcd.example.com",
            "test-1",
            wire,
        )
        assert out["ok"] is True

    def test_xrp_via_rpc_mock(self, monkeypatch):
        k = _toy_key()
        v = StateVerifier(k)
        x = XrpLedgerCommitment("xrpl-testnet", 55, "0x" + "22" * 32)
        cert = v.issue_for_anchor(x, _rng(8))
        wire = cert.to_wire_dict()

        def fake_fetch(
            rpc_url: str,
            *,
            network_id: str,
            ledger_index="validated",
            timeout: float = 30.0,
        ):
            assert "xrpl.example" in rpc_url
            assert network_id == "xrpl-testnet"
            return x

        monkeypatch.setattr(chain_api_mod, "fetch_xrp_ledger_commitment", fake_fetch)
        out = verify_xrp_state_certificate_via_rpc(
            "https://xrpl.example/",
            wire,
            network_id="xrpl-testnet",
        )
        assert out["ok"] is True

    def test_xrp_jsonrpc_parses_ledger(self, monkeypatch):
        def fake_jsonrpc(rpc_url, method, params, timeout=30.0):
            assert method == "ledger"
            return {
                "ledger": {
                    "ledger_index": 42,
                    "ledger_hash": "AA" * 32,
                }
            }

        monkeypatch.setattr(xrp_rpc_mod, "jsonrpc_call", fake_jsonrpc)
        from statecert.xrp_rpc import fetch_xrp_ledger_commitment

        c = fetch_xrp_ledger_commitment(
            "https://s1.ripple.com",
            network_id="xrpl-mainnet",
            ledger_index=42,
        )
        assert c.ledger_index == 42
        assert c.ledger_hash_hex == "0x" + "aa" * 32
