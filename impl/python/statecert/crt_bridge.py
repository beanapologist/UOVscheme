"""Python mirror of ``CRTBridge.lean``: coprime encode/decode on ``Z/(mn)Z``."""

from __future__ import annotations

import math
from typing import Tuple


class CRTBridge:
    """Encode ``a mod (m*n)`` as ``(a mod m, a mod n)`` and decode back when ``gcd(m,n)=1``."""

    __slots__ = ("m", "n")

    def __init__(self, m: int, n: int) -> None:
        if m < 1 or n < 1:
            raise ValueError("m and n must be positive")
        if math.gcd(m, n) != 1:
            raise ValueError("CRT requires coprime moduli")
        self.m = m
        self.n = n

    @property
    def mn(self) -> int:
        return self.m * self.n

    def encode(self, a: int) -> Tuple[int, int]:
        """``a : Z/(mn)Z`` → residues ``(a mod m, a mod n)``."""
        a = a % self.mn
        return (a % self.m, a % self.n)

    def decode(self, am: int, an: int) -> int:
        """Glue ``(am, an)`` to the unique class ``mod (m*n)`` (CRT inverse)."""
        am %= self.m
        an %= self.n
        # Solve x ≡ am (mod m), x ≡ an (mod n)  →  x = am + m*t,  m*t ≡ an-am (mod n)
        inv_m_mod_n = pow(self.m, -1, self.n)
        t = ((an - am) % self.n) * inv_m_mod_n % self.n
        return (am + self.m * t) % self.mn
