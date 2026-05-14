"""Digest binding for multi-ecosystem anchors."""

from __future__ import annotations

import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from statecert.state_hash import (
    ChainState,
    CosmosCommitment,
    CrossL1Commitment,
    SolanaCommitment,
    anchor_to_digest,
    intra_cosmos_height_transition_to_digest,
    intra_solana_slot_transition_to_digest,
)


def test_anchor_digest_stable_evm():
    s = ChainState("eip155:1", 1, "0x" + "aa" * 32)
    y1 = anchor_to_digest(31, 4, s)
    y2 = anchor_to_digest(31, 4, s)
    assert y1 == y2 and len(y1) == 4


def test_cross_l1_mixed_digest():
    evm = ChainState("eip155:1", 10, "0x" + "01" * 32)
    sol = SolanaCommitment(
        "mainnet-beta", 99, "SoLHaShExAmPlExxxxxxxxxxxxxxxxxxxxxxxxxxxxx"
    )
    x = CrossL1Commitment(src=evm, dst=sol)
    y = anchor_to_digest(31, 4, x)
    assert len(y) == 4


def test_intra_solana_requires_same_cluster():
    a = SolanaCommitment("devnet", 1, "A")
    b = SolanaCommitment("mainnet-beta", 2, "B")
    try:
        intra_solana_slot_transition_to_digest(31, 4, a, b)
    except ValueError as e:
        assert "cluster_id" in str(e)
    else:
        raise AssertionError("expected ValueError")


def test_intra_cosmos_requires_same_chain_id():
    a = CosmosCommitment("hub-4", 1, "0x01")
    b = CosmosCommitment("hub-5", 2, "0x02")
    try:
        intra_cosmos_height_transition_to_digest(31, 4, a, b)
    except ValueError as e:
        assert "chain_id" in str(e)
    else:
        raise AssertionError("expected ValueError")
