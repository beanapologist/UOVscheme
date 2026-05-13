"""Key generation for the UOV signature scheme."""

from __future__ import annotations

from typing import Optional

from .central_map import CentralMap
from .field import gf_random_invertible, gf_matinv
from .params import validate_uov_params
from .rng import FieldRng, SecretsRng
from .scheme import UOVKey


def keygen(
    q: int,
    o: int,
    v: int,
    *,
    rng: Optional[FieldRng] = None,
    allow_toy_params: bool = False,
) -> UOVKey:
    """Generate a UOV key pair over GF(q) with o oil and v vinegar variables.

    Uses OS CSPRNG via :class:`SecretsRng` when ``rng`` is omitted.

    Parameters
    ----------
    allow_toy_params:
        If True, allow vinegar spaces smaller than ~128 bits (emits
        :class:`UserWarning`). Demos and unit tests should set this; application
        code targeting real security should use adequate (q, o, v) and leave
        this False.
    """
    validate_uov_params(q, o, v, allow_toy_params=allow_toy_params)
    if rng is None:
        rng = SecretsRng()
    F = CentralMap.random(q, o, v, rng)
    T = gf_random_invertible(o + v, q, rng)
    T_inv = gf_matinv(T, q)
    assert T_inv is not None
    return UOVKey(q=q, o=o, v=v, F=F, T=T, T_inv=T_inv)
