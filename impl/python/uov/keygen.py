"""Key generation for the UOV signature scheme."""

import random
from .central_map import CentralMap
from .field import gf_random_invertible, gf_matinv
from .scheme import UOVKey


def keygen(q: int, o: int, v: int, seed: int = None) -> UOVKey:
    """Generate a fresh UOV key pair over GF(q) with o oil and v vinegar variables."""
    rng = random.Random(seed)
    F = CentralMap.random(q, o, v, rng)
    T = gf_random_invertible(o + v, q, rng)
    T_inv = gf_matinv(T, q)
    return UOVKey(q=q, o=o, v=v, F=F, T=T, T_inv=T_inv)
