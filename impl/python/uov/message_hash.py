"""Hash messages to GF(q)^o for hash-then-sign (SHAKE256, domain-separated)."""

from __future__ import annotations

import hashlib
import struct
from typing import List

_DOMAIN = b"UOVscheme/v1|"


def _uniform_mod_q(stream: memoryview, q: int, o: int) -> List[int]:
    """Draw o independent uniform elements in [0,q) via rejection (unbiased)."""
    if q < 2:
        raise ValueError("q must be >= 2")
    max_valid = (1 << 64) // q * q
    out: List[int] = []
    pos = 0
    while len(out) < o:
        need = 8
        if pos + need > len(stream):
            raise ValueError("internal: insufficient XOF output for rejection sampling")
        chunk = int.from_bytes(stream[pos : pos + 8], "big")
        pos += 8
        if chunk < max_valid:
            out.append(chunk % q)
    return out


def hash_message_to_digest(q: int, o: int, message: bytes) -> List[int]:
    """Map ``message`` to ``y in GF(q)^o`` using SHAKE256 XOF.

    Domain separation: prefix ``UOVscheme/v1|``, 8-byte big-endian length of
    ``message``, then ``message``. Output bytes are consumed in 8-byte chunks
    with rejection so each coordinate is (exactly) uniform on ``Z/qZ`` when
    the XOF is modeled as random (standard encode-then-reject).
    """
    if o < 1:
        raise ValueError("o must be positive")
    h = hashlib.shake_256()
    h.update(_DOMAIN)
    h.update(struct.pack(">Q", len(message)))
    h.update(message)
    # Worst-case rejections: reserve generous output (each slot rarely needs many tries)
    nbytes = o * 8 * 16
    buf = h.digest(nbytes)
    return _uniform_mod_q(memoryview(buf), q, o)
