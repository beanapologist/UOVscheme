"""Canonical chain state bytes → SHA-256 → GF(q)^o digest ``y`` (domain-separated XOF)."""

from __future__ import annotations

import hashlib
import json
import struct
from dataclasses import dataclass
from typing import Any, Dict, List, Union

# Domain tag for expanding a 32-byte SHA-256 digest into field coordinates.
_FIELD_DOMAIN = b"statecert/state-to-field/v1|"


def _uniform_mod_q(stream: memoryview, q: int, o: int) -> List[int]:
    """Draw ``o`` independent elements in ``[0,q)`` via 8-byte rejection (same as ``uov.message_hash``)."""
    if q < 2:
        raise ValueError("q must be >= 2")
    if o < 1:
        raise ValueError("o must be positive")
    max_valid = (1 << 64) // q * q
    out: List[int] = []
    pos = 0
    nbytes = len(stream)
    while len(out) < o:
        if pos + 8 > nbytes:
            raise ValueError("internal: insufficient XOF output for rejection sampling")
        chunk = int.from_bytes(stream[pos : pos + 8], "big")
        pos += 8
        if chunk < max_valid:
            out.append(chunk % q)
    return out


def _sha256_digest_bytes(obj: Dict[str, Any]) -> bytes:
    """Deterministic JSON → SHA-256 (32 bytes)."""
    canonical = json.dumps(obj, sort_keys=True, separators=(",", ":")).encode()
    return hashlib.sha256(canonical).digest()


def sha256_preimage_to_digest(q: int, o: int, sha256_32: bytes) -> List[int]:
    """Map a 32-byte SHA-256 digest to ``y ∈ GF(q)^o`` using SHAKE256 + rejection."""
    if len(sha256_32) != 32:
        raise ValueError("expected 32-byte SHA-256 digest")
    h = hashlib.shake_256()
    h.update(_FIELD_DOMAIN)
    h.update(struct.pack(">Q", 32))
    h.update(sha256_32)
    buf = h.digest(o * 8 * 16)
    return _uniform_mod_q(memoryview(buf), q, o)


@dataclass(frozen=True)
class ChainState:
    """Single-chain anchor (e.g. one L1 or one rollup)."""

    chain_id: str
    block_height: int
    state_root_hex: str

    def to_canonical_dict(self) -> Dict[str, Any]:
        return {
            "kind": "ChainState",
            "chain_id": self.chain_id,
            "block_height": int(self.block_height),
            "state_root_hex": self.state_root_hex.lower(),
        }


@dataclass(frozen=True)
class CrossChainStateTransition:
    """Cross-chain pair: observed roots on source and destination."""

    src: ChainState
    dst: ChainState

    def to_canonical_dict(self) -> Dict[str, Any]:
        return {
            "kind": "CrossChainStateTransition",
            "src": self.src.to_canonical_dict(),
            "dst": self.dst.to_canonical_dict(),
        }


@dataclass(frozen=True)
class SolanaCommitment:
    """Solana L1 anchor: finalized slot + blockhash (base58, case-sensitive)."""

    cluster_id: str
    slot: int
    blockhash_b58: str

    def to_canonical_dict(self) -> Dict[str, Any]:
        return {
            "kind": "SolanaCommitment",
            "cluster_id": self.cluster_id,
            "slot": int(self.slot),
            "blockhash_b58": self.blockhash_b58,
        }


@dataclass(frozen=True)
class CosmosCommitment:
    """Tendermint / Cosmos-SDK style anchor (LCD block header ``app_hash``)."""

    chain_id: str
    height: int
    app_hash_hex: str

    def to_canonical_dict(self) -> Dict[str, Any]:
        h = self.app_hash_hex.strip().lower()
        hx = h if h.startswith("0x") else "0x" + h
        return {
            "kind": "CosmosCommitment",
            "chain_id": self.chain_id,
            "height": int(self.height),
            "app_hash_hex": hx,
        }


@dataclass(frozen=True)
class XrpLedgerCommitment:
    """XRPL (rippled) anchor: validated ledger index + ``ledger_hash`` (hex, ``0x``-prefixed)."""

    network_id: str
    ledger_index: int
    ledger_hash_hex: str

    def to_canonical_dict(self) -> Dict[str, Any]:
        h = self.ledger_hash_hex.strip().lower()
        hx = h if h.startswith("0x") else "0x" + h
        return {
            "kind": "XrpLedgerCommitment",
            "network_id": self.network_id,
            "ledger_index": int(self.ledger_index),
            "ledger_hash_hex": hx,
        }


@dataclass(frozen=True)
class CrossL1Commitment:
    """Two single-chain anchors from possibly different ecosystems (EVM / Solana / Cosmos / XRPL)."""

    src: Union[ChainState, SolanaCommitment, CosmosCommitment, XrpLedgerCommitment]
    dst: Union[ChainState, SolanaCommitment, CosmosCommitment, XrpLedgerCommitment]

    def to_canonical_dict(self) -> Dict[str, Any]:
        return {
            "kind": "CrossL1Commitment",
            "src": _anchor_to_dict(self.src),
            "dst": _anchor_to_dict(self.dst),
        }


def _anchor_to_dict(
    a: Union[ChainState, SolanaCommitment, CosmosCommitment, XrpLedgerCommitment],
) -> Dict[str, Any]:
    return a.to_canonical_dict()


ChainAnchor = Union[
    ChainState,
    SolanaCommitment,
    CosmosCommitment,
    XrpLedgerCommitment,
    CrossL1Commitment,
]


def anchor_to_digest(q: int, o: int, anchor: ChainAnchor) -> List[int]:
    """Map any supported anchor object to ``y ∈ GF(q)^o``."""
    return sha256_preimage_to_digest(
        q, o, _sha256_digest_bytes(anchor.to_canonical_dict())
    )


def chain_state_to_digest(q: int, o: int, state: ChainState) -> List[int]:
    """``ChainState`` → canonical JSON → SHA-256 → ``y ∈ GF(q)^o``."""
    return anchor_to_digest(q, o, state)


def cross_chain_to_digest(q: int, o: int, x: CrossChainStateTransition) -> List[int]:
    """Cross-chain transition → ``y``."""
    return sha256_preimage_to_digest(q, o, _sha256_digest_bytes(x.to_canonical_dict()))


def intra_chain_transition_to_digest(
    q: int, o: int, prev: ChainState, nxt: ChainState
) -> List[int]:
    """Same ``chain_id``: block ``N`` → ``N+1`` (or any ordered pair on one chain)."""
    if prev.chain_id != nxt.chain_id:
        raise ValueError("intra-chain transition requires matching chain_id")
    body = {
        "kind": "IntraChainStateTransition",
        "chain_id": prev.chain_id,
        "prev": prev.to_canonical_dict(),
        "next": nxt.to_canonical_dict(),
    }
    return sha256_preimage_to_digest(q, o, _sha256_digest_bytes(body))


def solana_commitment_to_digest(q: int, o: int, s: SolanaCommitment) -> List[int]:
    return anchor_to_digest(q, o, s)


def cosmos_commitment_to_digest(q: int, o: int, c: CosmosCommitment) -> List[int]:
    return anchor_to_digest(q, o, c)


def xrp_commitment_to_digest(q: int, o: int, x: XrpLedgerCommitment) -> List[int]:
    return anchor_to_digest(q, o, x)


def cross_l1_commitment_to_digest(q: int, o: int, x: CrossL1Commitment) -> List[int]:
    return anchor_to_digest(q, o, x)


def intra_solana_slot_transition_to_digest(
    q: int, o: int, prev: SolanaCommitment, nxt: SolanaCommitment
) -> List[int]:
    if prev.cluster_id != nxt.cluster_id:
        raise ValueError(
            "intra-Solana transition requires matching cluster_id on prev and next"
        )
    body = {
        "kind": "IntraSolanaSlotTransition",
        "cluster_id": prev.cluster_id,
        "prev": prev.to_canonical_dict(),
        "next": nxt.to_canonical_dict(),
    }
    return sha256_preimage_to_digest(q, o, _sha256_digest_bytes(body))


def intra_cosmos_height_transition_to_digest(
    q: int, o: int, prev: CosmosCommitment, nxt: CosmosCommitment
) -> List[int]:
    if prev.chain_id != nxt.chain_id:
        raise ValueError(
            "intra-Cosmos transition requires matching chain_id on prev and next"
        )
    body = {
        "kind": "IntraCosmosHeightTransition",
        "chain_id": prev.chain_id,
        "prev": prev.to_canonical_dict(),
        "next": nxt.to_canonical_dict(),
    }
    return sha256_preimage_to_digest(q, o, _sha256_digest_bytes(body))
