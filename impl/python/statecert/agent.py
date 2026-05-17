"""Agent PKI: canonical agent identity → field digest → UOV state certificate."""

from __future__ import annotations

import time
from dataclasses import dataclass
from typing import Any, Dict, List, Optional

from .state_hash import _sha256_digest_bytes, sha256_preimage_to_digest


@dataclass(frozen=True)
class AgentIdentity:
    """Claims bound into an agent certificate (Agent PKI v1)."""

    agent_did: str
    capabilities: Dict[str, Any]
    reputation_hash: Optional[str] = None
    anchor: Optional[Dict[str, Any]] = None
    expires_at_unix: Optional[int] = None

    def to_canonical_dict(self) -> Dict[str, Any]:
        if not self.agent_did.strip():
            raise ValueError("agent_did must be non-empty")
        if not isinstance(self.capabilities, dict):
            raise ValueError("capabilities must be a JSON object")
        out: Dict[str, Any] = {
            "kind": "AgentIdentity",
            "schema": "silentverify.agent_identity/v1",
            "agent_did": self.agent_did.strip(),
            "capabilities": self.capabilities,
        }
        if self.reputation_hash is not None:
            out["reputation_hash"] = str(self.reputation_hash)
        if self.anchor is not None:
            if not isinstance(self.anchor, dict):
                raise ValueError("anchor must be a JSON object when present")
            out["anchor"] = self.anchor
        if self.expires_at_unix is not None:
            out["expires_at_unix"] = int(self.expires_at_unix)
        return out


def agent_identity_to_digest(q: int, o: int, identity: AgentIdentity) -> List[int]:
    """Map canonical agent identity JSON → ``y ∈ GF(q)^o`` (same path as chain state)."""
    preimage = _sha256_digest_bytes(identity.to_canonical_dict())
    return sha256_preimage_to_digest(q, o, preimage)


def agent_identity_from_request(
    *,
    agent_did: str,
    capabilities: Dict[str, Any],
    reputation_hash: Optional[str] = None,
    anchor: Optional[Dict[str, Any]] = None,
    expires_in_days: int = 30,
) -> AgentIdentity:
    """Build identity with ``expires_at_unix`` from ``expires_in_days`` (UTC wall clock)."""
    if expires_in_days < 1:
        raise ValueError("expires_in_days must be >= 1")
    if expires_in_days > 3650:
        raise ValueError("expires_in_days must be <= 3650")
    now = int(time.time())
    expires_at = now + int(expires_in_days) * 86400
    return AgentIdentity(
        agent_did=agent_did,
        capabilities=capabilities,
        reputation_hash=reputation_hash,
        anchor=anchor,
        expires_at_unix=expires_at,
    )
