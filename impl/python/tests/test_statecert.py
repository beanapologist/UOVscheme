"""Tests for ``statecert`` pipeline (state hash, CRT bridge, certificates)."""

from __future__ import annotations

import os
import random
import sys
import warnings

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from statecert import (
    CRTBridge,
    ChainState,
    CrossChainStateTransition,
    CrossL1Commitment,
    SolanaCommitment,
    StateCertificate,
    StateVerifier,
    chain_state_to_digest,
    intra_chain_transition_to_digest,
)
from uov import RandomAdapter, keygen
from uov.certificate import public_key_wire


def rng(seed: int = 0) -> RandomAdapter:
    return RandomAdapter(random.Random(seed))


def toy_key(seed: int = 1):
    with warnings.catch_warnings():
        warnings.simplefilter("ignore", UserWarning)
        return keygen(31, 4, 8, rng=rng(seed), allow_toy_params=True)


# ── state hash ──────────────────────────────────────────────────────────────


class TestStateHash:
    def test_digest_length(self):
        k = toy_key()
        cs = ChainState("ethereum:1", 18_000_000, "0xabc")
        y = chain_state_to_digest(k.q, k.o, cs)
        assert len(y) == k.o

    def test_xrp_digest_length(self):
        from statecert.state_hash import XrpLedgerCommitment, xrp_commitment_to_digest

        k = toy_key()
        x = XrpLedgerCommitment("xrpl-mainnet", 80_000_000, "0x" + "ab" * 32)
        y = xrp_commitment_to_digest(k.q, k.o, x)
        assert len(y) == k.o

    def test_digest_range(self):
        k = toy_key()
        cs = ChainState("solana:mainnet", 300_000_000, "deadbeef")
        y = chain_state_to_digest(k.q, k.o, cs)
        assert all(0 <= x < k.q for x in y)

    def test_determinism(self):
        k = toy_key()
        cs = ChainState("ethereum:1", 1, "0xaa")
        assert chain_state_to_digest(k.q, k.o, cs) == chain_state_to_digest(
            k.q, k.o, cs
        )

    def test_sensitivity_block_height(self):
        k = toy_key()
        a = ChainState("ethereum:1", 100, "0xroot")
        b = ChainState("ethereum:1", 101, "0xroot")
        assert chain_state_to_digest(k.q, k.o, a) != chain_state_to_digest(k.q, k.o, b)


# ── CRT bridge ───────────────────────────────────────────────────────────────


class TestCRTBridge:
    def test_decode_encode(self):
        br = CRTBridge(7, 11)
        for a in [0, 1, 42, br.mn - 1]:
            assert br.decode(*br.encode(a)) == a % br.mn

    def test_encode_decode(self):
        br = CRTBridge(7, 11)
        for am in range(7):
            for an in range(11):
                p = br.encode(br.decode(am, an))
                assert p == (am, an)

    def test_coprime_guard(self):
        import pytest

        with pytest.raises(ValueError, match="coprime"):
            CRTBridge(6, 9)

    def test_global_state_locking(self):
        """Two coprime views determine a unique global residue."""
        br = CRTBridge(13, 17)
        seen = {}
        for a in range(br.mn):
            pair = br.encode(a)
            assert pair not in seen or seen[pair] == a % br.mn
            seen[pair] = a % br.mn


# ── single-chain certificate ─────────────────────────────────────────────────


class TestSingleChainCertificate:
    def test_issue_and_verify(self):
        k = toy_key()
        v = StateVerifier(k)
        cs = ChainState("ethereum:1", 12_345, "0xstate")
        cert = v.issue_for_chain_state(cs, rng(2))
        assert StateVerifier.verify_certificate(cert)
        assert cert.verify_crypto()


# ── cross-chain (Ethereum → Solana toy IDs) ───────────────────────────────────


class TestCrossChainCertificate:
    def test_cross_chain_verify(self):
        k = toy_key()
        v = StateVerifier(k)
        eth = ChainState("ethereum:1", 19_000_000, "0xethroot")
        sol = ChainState("solana:mainnet", 250_000_000, "0xsolroot")
        x = CrossChainStateTransition(eth, sol)
        cert = v.issue_for_cross_chain(x, rng(3), metadata={"pair": "eth-sol"})
        assert cert.metadata.get("pair") == "eth-sol"
        assert StateVerifier.verify_certificate(cert)


# ── intra-chain (block N → N+1) ─────────────────────────────────────────────


class TestIntraChainCertificate:
    def test_intra_chain_verify(self):
        k = toy_key()
        v = StateVerifier(k)
        prev = ChainState("ethereum:1", 100, "0xaa")
        nxt = ChainState("ethereum:1", 101, "0xbb")
        cert = v.issue_for_intra_chain(prev, nxt, rng(4))
        assert StateVerifier.verify_certificate(cert)


# ── tamper + wrong key ──────────────────────────────────────────────────────


class TestTamperAndKeys:
    def test_flipped_message_digest_invalidates(self):
        k = toy_key()
        v = StateVerifier(k)
        cs = ChainState("ethereum:1", 7, "0xm")
        cert = v.issue_for_chain_state(cs, rng(5))
        inner = cert.inner
        inner.digest_y = [(inner.digest_y[0] + 1) % k.q] + inner.digest_y[1:]
        assert not StateVerifier.verify_certificate(cert)

    def test_flipped_sigma_invalidates(self):
        k = toy_key()
        v = StateVerifier(k)
        cert = v.issue_for_chain_state(ChainState("x", 1, "0x1"), rng(6))
        inner = cert.inner
        inner.sigma = [(inner.sigma[0] + 1) % k.q] + inner.sigma[1:]
        assert not StateVerifier.verify_certificate(cert)

    def test_wrong_key_rejects(self):
        k1, k2 = toy_key(10), toy_key(11)
        v1 = StateVerifier(k1)
        cert = v1.issue_for_chain_state(ChainState("c", 1, "0xa"), rng(7))
        inner = cert.inner
        inner.public_key = public_key_wire(k2)
        # Stale fingerprint still refers to k1's public key material
        assert not cert.verify()


class TestCrossL1Certificate:
    def test_issue_evm_to_solana(self):
        k = toy_key()
        v = StateVerifier(k)
        evm = ChainState("eip155:1", 1, "0x" + "22" * 32)
        sol = SolanaCommitment(
            "mainnet-beta", 9, "SoLmEmOxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx"
        )
        x = CrossL1Commitment(src=evm, dst=sol)
        cert = v.issue_for_cross_l1(x, rng(44), metadata={"bridge": "toy"})
        assert StateVerifier.verify_certificate(cert)


# ── JSON round-trip ──────────────────────────────────────────────────────────


class TestJsonRoundTrip:
    def test_certificate_survives_json(self):
        k = toy_key()
        v = StateVerifier(k)
        cert = v.issue_for_chain_state(
            ChainState("ethereum:1", 99, "0z"), rng(8), metadata={"n": 1}
        )
        js = cert.to_json(indent=None)
        cert2 = StateCertificate.from_json(js)
        assert StateVerifier.verify_certificate(cert2)


class TestPublicKeyFingerprint:
    def test_fp_stable(self):
        k = toy_key(20)
        fp1 = StateVerifier.public_key_fingerprint(k)
        fp2 = StateVerifier.public_key_fingerprint(k)
        assert fp1 == fp2 and len(fp1) == 64

    def test_fp_changes_with_key(self):
        k1, k2 = toy_key(21), toy_key(22)
        assert StateVerifier.public_key_fingerprint(
            k1
        ) != StateVerifier.public_key_fingerprint(k2)


class TestIntraChainValidation:
    def test_mismatched_chain_id_raises(self):
        k = toy_key()
        a = ChainState("eth", 1, "0x")
        b = ChainState("sol", 2, "0y")
        import pytest

        with pytest.raises(ValueError, match="chain_id"):
            intra_chain_transition_to_digest(k.q, k.o, a, b)
