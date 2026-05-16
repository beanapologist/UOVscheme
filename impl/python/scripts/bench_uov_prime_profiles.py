#!/usr/bin/env python3
"""Wall-clock benchmarks for this repo's **prime-field** UOV reference (Python).

This is **not** the NIST PQC UOV standard packaging over GF(2^k); it times the
profiles in ``uov.params`` (``NIST_STYLE_PRIME_*``) used by SilentVerify demos.

Run from repository root::

    python3 impl/python/scripts/bench_uov_prime_profiles.py
"""

from __future__ import annotations

import json
import os
import platform
import random
import sys
import time

# Allow ``python3 impl/python/scripts/...`` from repo root.
_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if _ROOT not in sys.path:
    sys.path.insert(0, _ROOT)

from uov.keygen import keygen  # noqa: E402
from uov.params import NIST_STYLE_PRIME_I_MIN, NIST_STYLE_PRIME_III  # noqa: E402
from uov.rng import RandomAdapter  # noqa: E402


def _bench_one(
    name: str,
    q: int,
    o: int,
    v: int,
    *,
    iterations: int,
    seed: int = 0,
) -> dict:
    rng_kg = RandomAdapter(random.Random(seed))
    t0 = time.perf_counter()
    key = keygen(q, o, v, rng=rng_kg)
    t_keygen = time.perf_counter() - t0

    y = [(i + 7) % q for i in range(o)]
    # Warmup (JIT / branch predictor friendly).
    w = key.sign(y, RandomAdapter(random.Random(seed + 1)))
    assert w is not None

    t1 = time.perf_counter()
    last_sigma = w
    for i in range(iterations):
        last_sigma = key.sign(y, RandomAdapter(random.Random(seed + 2 + i)))
        assert last_sigma is not None
    t_sign_total = time.perf_counter() - t1

    t2 = time.perf_counter()
    for _ in range(iterations):
        assert key.verify(y, last_sigma)
    t_verify_total = time.perf_counter() - t2

    return {
        "profile": name,
        "q": q,
        "o": o,
        "v": v,
        "iterations": iterations,
        "keygen_s": t_keygen,
        "sign_total_s": t_sign_total,
        "verify_total_s": t_verify_total,
        "sign_ms_per_op": 1000.0 * t_sign_total / iterations,
        "verify_ms_per_op": 1000.0 * t_verify_total / iterations,
    }


def main() -> None:
    meta = {
        "note": "Prime-field UOV in this repo; not NIST GF(2^k) UOV byte lengths.",
        "python": sys.version.split()[0],
        "platform": platform.platform(),
        "machine": platform.machine(),
        "processor": platform.processor() or "",
    }
    rows = [
        _bench_one("NIST_STYLE_PRIME_I_MIN", *NIST_STYLE_PRIME_I_MIN, iterations=80),
        _bench_one("NIST_STYLE_PRIME_III", *NIST_STYLE_PRIME_III, iterations=12),
    ]
    print(json.dumps({"environment": meta, "results": rows}, indent=2))


if __name__ == "__main__":
    main()
