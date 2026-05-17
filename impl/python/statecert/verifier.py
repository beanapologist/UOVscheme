"""``StateVerifier``: issue and verify certificates using a :class:`uov.scheme.UOVKey`."""

from __future__ import annotations

from typing import Any, Dict, List, Optional

from uov.certificate import issue_digest_certificate, public_key_wire
from uov.scheme import UOVKey

from .agent import AgentIdentity, agent_identity_to_digest
from .certificate import StateCertificate, fingerprint_public_key
from .state_hash import (
    ChainAnchor,
    ChainState,
    CosmosCommitment,
    CrossChainStateTransition,
    CrossL1Commitment,
    SolanaCommitment,
    XrpLedgerCommitment,
    anchor_to_digest,
    chain_state_to_digest,
    cosmos_commitment_to_digest,
    cross_chain_to_digest,
    cross_l1_commitment_to_digest,
    intra_chain_transition_to_digest,
    intra_cosmos_height_transition_to_digest,
    intra_solana_slot_transition_to_digest,
    solana_commitment_to_digest,
    xrp_commitment_to_digest,
)


class StateVerifier:
    """Holds a UOV key pair; builds field digests from chain models and issues certificates."""

    def __init__(self, key: UOVKey) -> None:
        self._key = key

    @property
    def key(self) -> UOVKey:
        return self._key

    def digest_for_chain_state(self, state: ChainState) -> List[int]:
        return chain_state_to_digest(self._key.q, self._key.o, state)

    def digest_for_anchor(self, anchor: ChainAnchor) -> List[int]:
        return anchor_to_digest(self._key.q, self._key.o, anchor)

    def digest_for_cross_chain(self, x: CrossChainStateTransition) -> List[int]:
        return cross_chain_to_digest(self._key.q, self._key.o, x)

    def digest_for_cross_l1(self, x: CrossL1Commitment) -> List[int]:
        return cross_l1_commitment_to_digest(self._key.q, self._key.o, x)

    def digest_for_solana(self, s: SolanaCommitment) -> List[int]:
        return solana_commitment_to_digest(self._key.q, self._key.o, s)

    def digest_for_cosmos(self, c: CosmosCommitment) -> List[int]:
        return cosmos_commitment_to_digest(self._key.q, self._key.o, c)

    def digest_for_xrp(self, x: XrpLedgerCommitment) -> List[int]:
        return xrp_commitment_to_digest(self._key.q, self._key.o, x)

    def digest_for_intra_solana(
        self, prev: SolanaCommitment, nxt: SolanaCommitment
    ) -> List[int]:
        return intra_solana_slot_transition_to_digest(
            self._key.q, self._key.o, prev, nxt
        )

    def digest_for_intra_cosmos(
        self, prev: CosmosCommitment, nxt: CosmosCommitment
    ) -> List[int]:
        return intra_cosmos_height_transition_to_digest(
            self._key.q, self._key.o, prev, nxt
        )

    def digest_for_intra_chain(self, prev: ChainState, nxt: ChainState) -> List[int]:
        return intra_chain_transition_to_digest(self._key.q, self._key.o, prev, nxt)

    def digest_for_agent(self, identity: AgentIdentity) -> List[int]:
        return agent_identity_to_digest(self._key.q, self._key.o, identity)

    def issue_for_agent(
        self,
        identity: AgentIdentity,
        rng,
        metadata: Optional[Dict[str, Any]] = None,
    ) -> StateCertificate:
        md = {
            "flow": "agent_pki",
            "cert_type": "agent",
            "agent_did": identity.agent_did,
            **(metadata or {}),
        }
        if identity.expires_at_unix is not None:
            md["expires_at_unix"] = identity.expires_at_unix
        return self.issue_on_digest(self.digest_for_agent(identity), rng, md)

    def issue_on_digest(
        self, digest_y: List[int], rng, metadata: Optional[Dict[str, Any]] = None
    ) -> StateCertificate:
        inner = issue_digest_certificate(self._key, digest_y, rng)
        fp = fingerprint_public_key(inner.public_key)
        return StateCertificate(
            inner=inner, pubkey_fp=fp, metadata=dict(metadata or {})
        )

    def issue_for_chain_state(
        self, state: ChainState, rng, metadata: Optional[Dict[str, Any]] = None
    ) -> StateCertificate:
        return self.issue_on_digest(self.digest_for_chain_state(state), rng, metadata)

    def issue_for_anchor(
        self, anchor: ChainAnchor, rng, metadata: Optional[Dict[str, Any]] = None
    ) -> StateCertificate:
        return self.issue_on_digest(self.digest_for_anchor(anchor), rng, metadata)

    def issue_for_cross_chain(
        self,
        x: CrossChainStateTransition,
        rng,
        metadata: Optional[Dict[str, Any]] = None,
    ) -> StateCertificate:
        md = {"flow": "cross_chain", **(metadata or {})}
        return self.issue_on_digest(self.digest_for_cross_chain(x), rng, md)

    def issue_for_cross_l1(
        self, x: CrossL1Commitment, rng, metadata: Optional[Dict[str, Any]] = None
    ) -> StateCertificate:
        md = {"flow": "cross_l1", **(metadata or {})}
        return self.issue_on_digest(self.digest_for_cross_l1(x), rng, md)

    def issue_for_solana(
        self, s: SolanaCommitment, rng, metadata: Optional[Dict[str, Any]] = None
    ) -> StateCertificate:
        return self.issue_for_anchor(s, rng, metadata)

    def issue_for_cosmos(
        self, c: CosmosCommitment, rng, metadata: Optional[Dict[str, Any]] = None
    ) -> StateCertificate:
        return self.issue_for_anchor(c, rng, metadata)

    def issue_for_xrp(
        self, x: XrpLedgerCommitment, rng, metadata: Optional[Dict[str, Any]] = None
    ) -> StateCertificate:
        return self.issue_for_anchor(x, rng, metadata)

    def issue_for_intra_chain(
        self,
        prev: ChainState,
        nxt: ChainState,
        rng,
        metadata: Optional[Dict[str, Any]] = None,
    ) -> StateCertificate:
        md = {"flow": "intra_chain", **(metadata or {})}
        return self.issue_on_digest(self.digest_for_intra_chain(prev, nxt), rng, md)

    def issue_for_intra_solana(
        self,
        prev: SolanaCommitment,
        nxt: SolanaCommitment,
        rng,
        metadata: Optional[Dict[str, Any]] = None,
    ) -> StateCertificate:
        md = {"flow": "intra_solana", **(metadata or {})}
        return self.issue_on_digest(self.digest_for_intra_solana(prev, nxt), rng, md)

    def issue_for_intra_cosmos(
        self,
        prev: CosmosCommitment,
        nxt: CosmosCommitment,
        rng,
        metadata: Optional[Dict[str, Any]] = None,
    ) -> StateCertificate:
        md = {"flow": "intra_cosmos", **(metadata or {})}
        return self.issue_on_digest(self.digest_for_intra_cosmos(prev, nxt), rng, md)

    @staticmethod
    def verify_certificate(cert: StateCertificate) -> bool:
        """Stateless check (public key + ``σ`` only inside ``cert``)."""
        return cert.verify()

    @staticmethod
    def public_key_fingerprint(key: UOVKey) -> str:
        return fingerprint_public_key(public_key_wire(key))
