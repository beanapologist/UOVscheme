"""SaaS issuer: load root UOV key from environment (dev seed or keygen profile)."""

from __future__ import annotations

import os
import random
from functools import lru_cache
from typing import Tuple

from uov import RandomAdapter, keygen
from uov.params import NIST_STYLE_PRIME_I_MIN, nist_style_prime_params
from uov.scheme import UOVKey

from .verifier import StateVerifier


def _parse_profile() -> Tuple[int, int, int]:
    default = (
        "I_MIN"
        if os.environ.get("SILENTVERIFY_ENV", "").lower() in ("production", "prod")
        else "TOY"
    )
    level = os.environ.get("SILENTVERIFY_UOV_PROFILE", default).strip()
    if level == "TOY":
        return (31, 4, 8)
    return nist_style_prime_params(level)


@lru_cache(maxsize=1)
def load_root_key() -> UOVKey:
    """Deterministic issuer key from ``SILENTVERIFY_ISSUER_SEED`` (default ``42``)."""
    q, o, v = _parse_profile()
    seed = int(os.environ.get("SILENTVERIFY_ISSUER_SEED", "42"))
    rng = RandomAdapter(random.Random(seed))
    allow_toy = q <= 31
    return keygen(q, o, v, rng=rng, allow_toy_params=allow_toy)


@lru_cache(maxsize=1)
def load_verifier() -> StateVerifier:
    return StateVerifier(load_root_key())


def recommended_params() -> dict:
    q, o, v = NIST_STYLE_PRIME_I_MIN
    return {
        "recommended": {"q": q, "o": o, "v": v, "profile": "I_MIN"},
        "toy_dev_only": {"q": 31, "o": 4, "v": 8, "profile": "TOY"},
        "note": (
            "Prime-field UOV profiles for this codebase; not byte-identical to NIST GF(2^k) OV-*."
        ),
    }
