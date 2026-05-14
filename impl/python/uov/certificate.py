"""Versioned state certificates: JSON wire format + issue / verify pipeline.

Schema ``silentverify.state_cert/v1`` carries a digest ``y``, signature ``sigma``,
and **public** key material (``q``, ``o``, ``v``, central map ``F``, matrix ``T``)
so verifiers never need ``T_inv``.  Issuance requires a full :class:`UOVKey`.
"""

from __future__ import annotations

import base64
import hashlib
import json
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional

from .central_map import CentralMap, CentralMapComp
from .field import gf_matinv
from .message_hash import hash_message_to_digest
from .scheme import UOVKey


SCHEMA_V1 = "silentverify.state_cert/v1"
# Legacy identifiers (still accepted when parsing JSON).
SCHEMA_LEGACY_FIELDCERT = "fieldcert.state_cert/v1"
SCHEMA_LEGACY_EIGENVERSE = "eigenverse.state_cert/v1"


def _comp_to_wire(c: CentralMapComp) -> Dict[str, Any]:
    return {
        "A": c.A,
        "B": c.B,
        "c": c.c,
        "d": c.d,
        "e": c.e,
    }


def _comp_from_wire(q: int, o: int, v: int, d: Dict[str, Any]) -> CentralMapComp:
    return CentralMapComp(
        q=q,
        o=o,
        v=v,
        A=d["A"],
        B=d["B"],
        c=d["c"],
        d=d["d"],
        e=int(d["e"]),
    )


def public_key_wire(key: UOVKey) -> Dict[str, Any]:
    """Serializable public material (no ``T_inv``)."""
    return {
        "q": key.q,
        "o": key.o,
        "v": key.v,
        "central_map": {"comps": [_comp_to_wire(c) for c in key.F.comps]},
        "T": key.T,
    }


def uovkey_from_public_wire(d: Dict[str, Any]) -> UOVKey:
    """Reconstruct a :class:`UOVKey` for verification-only use (computes ``T_inv``)."""
    q, o, v = int(d["q"]), int(d["o"]), int(d["v"])
    comps_data = d["central_map"]["comps"]
    F = CentralMap(
        q=q,
        o=o,
        v=v,
        comps=[_comp_from_wire(q, o, v, c) for c in comps_data],
    )
    T = d["T"]
    T_inv = gf_matinv(T, q)
    if T_inv is None:
        raise ValueError("public key matrix T is singular")
    return UOVKey(q=q, o=o, v=v, F=F, T=T, T_inv=T_inv)


@dataclass
class StateCertificateV1:
    """In-memory certificate (schema v1)."""

    q: int
    o: int
    v: int
    digest_y: List[int]
    sigma: List[int]
    public_key: Dict[str, Any]
    message_sha256_hex: Optional[str] = None
    schema_version: str = field(default=SCHEMA_V1, init=False)

    def to_wire_dict(self) -> Dict[str, Any]:
        out: Dict[str, Any] = {
            "schema_version": SCHEMA_V1,
            "q": self.q,
            "o": self.o,
            "v": self.v,
            "digest_y": self.digest_y,
            "sigma": self.sigma,
            "public_key": self.public_key,
        }
        if self.message_sha256_hex is not None:
            out["message_sha256_hex"] = self.message_sha256_hex
        return out

    def to_json(self, *, indent: Optional[int] = 2) -> str:
        return json.dumps(self.to_wire_dict(), indent=indent)

    @staticmethod
    def from_wire_dict(d: Dict[str, Any]) -> "StateCertificateV1":
        sv = d.get("schema_version")
        if sv not in (SCHEMA_V1, SCHEMA_LEGACY_FIELDCERT, SCHEMA_LEGACY_EIGENVERSE):
            raise ValueError(f"unsupported schema_version: {sv!r}")
        cert = StateCertificateV1(
            q=int(d["q"]),
            o=int(d["o"]),
            v=int(d["v"]),
            digest_y=list(d["digest_y"]),
            sigma=list(d["sigma"]),
            public_key=dict(d["public_key"]),
            message_sha256_hex=d.get("message_sha256_hex"),
        )
        return cert

    @staticmethod
    def from_json(s: str) -> "StateCertificateV1":
        return StateCertificateV1.from_wire_dict(json.loads(s))


def issue_digest_certificate(
    key: UOVKey, digest_y: List[int], rng
) -> StateCertificateV1:
    """Sign a raw digest ``y`` (already in ``GF(q)^o``)."""
    sig = key.sign(digest_y, rng)
    if sig is None:
        raise RuntimeError("signing failed (singular linear systems); retry")
    return StateCertificateV1(
        q=key.q,
        o=key.o,
        v=key.v,
        digest_y=list(digest_y),
        sigma=sig,
        public_key=public_key_wire(key),
    )


def issue_message_certificate(key: UOVKey, message: bytes, rng) -> StateCertificateV1:
    """Hash-then-sign: ``digest_y = H(message)``, then issue."""
    digest_y = hash_message_to_digest(key.q, key.o, message)
    cert = issue_digest_certificate(key, digest_y, rng)
    cert.message_sha256_hex = hashlib.sha256(message).hexdigest()
    return cert


def verify_certificate(cert: StateCertificateV1) -> bool:
    """Return True iff ``P(sigma) = digest_y`` under the embedded public key."""
    if cert.schema_version != SCHEMA_V1:
        return False
    if len(cert.digest_y) != cert.o or len(cert.sigma) != cert.o + cert.v:
        return False
    pk = dict(cert.public_key)
    try:
        vk = uovkey_from_public_wire(pk)
    except (KeyError, ValueError, TypeError):
        return False
    if vk.q != cert.q or vk.o != cert.o or vk.v != cert.v:
        return False
    return vk.verify(cert.digest_y, cert.sigma)


def message_matches_certificate(cert: StateCertificateV1, message: bytes) -> bool:
    """If ``message_sha256_hex`` is present, check it matches ``message``."""
    if cert.message_sha256_hex is None:
        return False
    return cert.message_sha256_hex == hashlib.sha256(message).hexdigest()


def b64encode_canonical(obj: Dict[str, Any]) -> str:
    """URL-safe base64 (no newlines) of minified JSON — handy for on-chain blobs."""
    raw = json.dumps(obj, separators=(",", ":"), sort_keys=True).encode()
    return base64.urlsafe_b64encode(raw).decode().rstrip("=")


def b64decode_canonical(token: str) -> Dict[str, Any]:
    pad = "=" * ((4 - len(token) % 4) % 4)
    raw = base64.urlsafe_b64decode(token + pad)
    return json.loads(raw.decode())


__all__ = [
    "SCHEMA_V1",
    "SCHEMA_LEGACY_FIELDCERT",
    "SCHEMA_LEGACY_EIGENVERSE",
    "StateCertificateV1",
    "public_key_wire",
    "uovkey_from_public_wire",
    "issue_digest_certificate",
    "issue_message_certificate",
    "verify_certificate",
    "message_matches_certificate",
    "b64encode_canonical",
    "b64decode_canonical",
]
