"""UOV parameter validation (prime q, v >= 2o, vinegar space size).

This repository implements UOV over a **prime** field ``ZMod q`` (see ``field.py``),
whereas the NIST PQC UOV standard uses primarily **extension fields** (e.g. ``GF(2^8)``).
The constants below are **prime-field reference profiles** that satisfy the same
structural constraint ``v >= 2*o`` and a conservative vinegar-space bit threshold
(≥128 bits, with stronger tiers documented inline). They are appropriate defaults
for the Python reference code and SilentVerify demos; they are **not** byte-for-byte
the NIST ``{Ip, Is, III, V}`` parameter sets from the standard document.
"""

from __future__ import annotations

import math
import warnings
from typing import Tuple

# Prime-field profiles (q, o, v) — see module docstring vs NIST GF(2^k) spec.
# Level names are *informal* security-size hints for this codebase only.
NIST_STYLE_PRIME_I_MIN: Tuple[int, int, int] = (251, 8, 24)  # ~191-bit vinegar space
NIST_STYLE_PRIME_III: Tuple[int, int, int] = (1009, 16, 40)  # ~400-bit vinegar space


def nist_style_prime_params(level: str = "I_MIN") -> Tuple[int, int, int]:
    """Return ``(q, o, v)`` for a named prime-field profile."""
    if level == "I_MIN":
        return NIST_STYLE_PRIME_I_MIN
    if level == "III":
        return NIST_STYLE_PRIME_III
    raise ValueError(f"unknown profile {level!r} (try 'I_MIN' or 'III')")


def is_prime(n: int) -> bool:
    if n < 2:
        return False
    if n in (2, 3, 5, 7):
        return True
    if n % 2 == 0:
        return False
    d = 3
    while d * d <= n:
        if n % d == 0:
            return False
        d += 2
    return True


def vinegar_space_bits(q: int, v: int) -> float:
    """Approximate log2(|GF(q)^v|) = v * log2(q)."""
    return v * math.log2(q)


def validate_uov_params(
    q: int,
    o: int,
    v: int,
    *,
    allow_toy_params: bool = False,
) -> None:
    """Raise ``ValueError`` if parameters are invalid for UOV.

    When the vinegar space has fewer than ~128 bits of entropy against
    exhaustion, either raises (default) or warns (if ``allow_toy_params``).
    """
    if o < 1 or v < 1:
        raise ValueError("o and v must be positive")
    if q < 2:
        raise ValueError("q must be at least 2")
    if not is_prime(q):
        raise ValueError(f"q={q} must be prime")
    if v < 2 * o:
        raise ValueError("require v >= 2*o (Kipnis–Shamir / UOV folklore)")
    bits = vinegar_space_bits(q, v)
    if bits < 128.0:
        msg = (
            f"vinegar space ~2^{bits:.1f} bits (<128); insecure for any real use. "
            "Use uov.params.NIST_STYLE_PRIME_I_MIN (or pass allow_toy_params=True for unit tests)."
        )
        if allow_toy_params:
            warnings.warn(msg, UserWarning, stacklevel=2)
        else:
            raise ValueError(msg)
