"""NIST-style **prime-field** profiles (see ``uov.params`` module docstring)."""

from __future__ import annotations

import os
import random
import sys

import pytest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from uov import RandomAdapter, keygen
from uov.params import (
    NIST_STYLE_PRIME_I_MIN,
    NIST_STYLE_PRIME_III,
    nist_style_prime_params,
)


def test_nist_style_prime_params_named():
    assert nist_style_prime_params("I_MIN") == NIST_STYLE_PRIME_I_MIN
    assert nist_style_prime_params("III") == NIST_STYLE_PRIME_III
    with pytest.raises(ValueError):
        nist_style_prime_params("nope")


def test_keygen_sign_verify_I_MIN():
    q, o, v = NIST_STYLE_PRIME_I_MIN
    rng = RandomAdapter(random.Random(101))
    key = keygen(q, o, v, rng=rng, allow_toy_params=False)
    y = [rng.randbelow(q) for _ in range(o)]
    sig = key.sign(y, rng)
    assert sig is not None and key.verify(y, sig)


def test_keygen_sign_verify_III():
    q, o, v = NIST_STYLE_PRIME_III
    rng = RandomAdapter(random.Random(303))
    key = keygen(q, o, v, rng=rng, allow_toy_params=False)
    y = [rng.randbelow(q) for _ in range(o)]
    sig = key.sign(y, rng)
    assert sig is not None and key.verify(y, sig)
