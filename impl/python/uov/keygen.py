"""
keygen.py — Random UOV key generation.

Recommended parameters (security level ≈ 128-bit against best known attacks):
  q=256 or q=31607, o=32, v=64   (roughly NIST UOV level 1)

For testing / learning, small parameters like q=7, o=4, v=8 are fine.
"""

from __future__ import annotations
import numpy as np
from .central_map import random_central_map
from .field import random_invertible_mat
from .scheme import UOVKey


def keygen(q: int, o: int, v: int, seed: int | None = None) -> UOVKey:
    """
    Generate a fresh UOV key pair over GF(q) with o oil and v vinegar vars.

    q must be prime.  Raises if T generation fails (astronomically unlikely).

    Returns
    -------
    UOVKey  containing the secret central map F and secret transform T.
            The public key is implicitly F ∘ T (accessed via key.public_eval).
    """
    rng = np.random.default_rng(seed)
    F   = random_central_map(q, o, v, rng)
    T   = random_invertible_mat(o + v, q, rng)
    return UOVKey(F, T)
