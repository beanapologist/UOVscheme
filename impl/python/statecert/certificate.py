"""Issued proof object: UOV ``StateCertificateV1`` plus fingerprint and metadata."""

from __future__ import annotations

import hashlib
import json
from dataclasses import dataclass, field
from typing import Any, Dict, Optional

from uov.certificate import (
    SCHEMA_LEGACY_EIGENVERSE,
    SCHEMA_LEGACY_FIELDCERT,
    SCHEMA_V1,
    StateCertificateV1,
    verify_certificate as uov_verify,
)


def fingerprint_public_key(public_key: Dict[str, Any]) -> str:
    """SHA-256 hex of canonical JSON of **public** key material (stable across runs)."""
    body = json.dumps(public_key, sort_keys=True, separators=(",", ":")).encode()
    return hashlib.sha256(body).hexdigest()


@dataclass
class StateCertificate:
    """Pipeline object: digest ``y``, signature ``σ``, public key, fingerprint, metadata."""

    inner: StateCertificateV1
    pubkey_fp: str
    metadata: Dict[str, Any] = field(default_factory=dict)

    @property
    def digest_y(self):
        return self.inner.digest_y

    @property
    def sigma(self):
        return self.inner.sigma

    def to_wire_dict(self) -> Dict[str, Any]:
        d = self.inner.to_wire_dict()
        d["pubkey_fp"] = self.pubkey_fp
        if self.metadata:
            d["metadata"] = dict(self.metadata)
        return d

    def to_json(self, *, indent: Optional[int] = 2) -> str:
        return json.dumps(self.to_wire_dict(), indent=indent)

    @staticmethod
    def from_wire_dict(d: Dict[str, Any]) -> "StateCertificate":
        if d.get("schema_version") not in (
            SCHEMA_V1,
            SCHEMA_LEGACY_FIELDCERT,
            SCHEMA_LEGACY_EIGENVERSE,
        ):
            raise ValueError(f"unsupported schema_version: {d.get('schema_version')!r}")
        inner = StateCertificateV1.from_wire_dict(
            {k: v for k, v in d.items() if k not in ("pubkey_fp", "metadata")}
        )
        fp = d.get("pubkey_fp")
        if fp is None:
            fp = fingerprint_public_key(inner.public_key)
        elif fp != fingerprint_public_key(inner.public_key):
            raise ValueError("pubkey_fp does not match embedded public key")
        meta = d.get("metadata") or {}
        if not isinstance(meta, dict):
            raise ValueError("metadata must be a JSON object")
        return StateCertificate(inner=inner, pubkey_fp=str(fp), metadata=dict(meta))

    @staticmethod
    def from_json(s: str) -> "StateCertificate":
        return StateCertificate.from_wire_dict(json.loads(s))

    def verify_crypto(self) -> bool:
        """``P(σ) = y`` under embedded public key."""
        return uov_verify(self.inner)

    def verify(self) -> bool:
        """Cryptographic check plus fingerprint consistency."""
        if self.pubkey_fp != fingerprint_public_key(self.inner.public_key):
            return False
        return self.verify_crypto()
