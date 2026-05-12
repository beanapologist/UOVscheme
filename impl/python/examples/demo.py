#!/usr/bin/env python3
"""Alice signs, Bob verifies, Eve fails — over GF(31) with o=4, v=8."""

import random
import sys

sys.path.insert(0, __file__.rsplit("/", 2)[0])

from uov import keygen


def main():
    q, o, v = 31, 4, 8
    print(f"UOV demo  q={q}  o={o}  v={v}  n={o + v}")
    print()

    # --- Key generation ---
    key = keygen(q, o, v, seed=42)
    print("Key generation: OK")

    # --- Alice signs ---
    rng = random.Random(1)
    msg = [rng.randrange(q) for _ in range(o)]
    sig = key.sign(msg, rng)
    assert sig is not None, "signing failed"
    print(f"Alice's message : {msg}")
    print(f"Alice's signature: {sig}")

    # --- Bob verifies ---
    ok = key.verify(msg, sig)
    print(f"Bob verifies    : {'PASS' if ok else 'FAIL'}")
    assert ok

    # --- Wrong message rejection ---
    wrong_msg = [(x + 1) % q for x in msg]
    print(
        f"Wrong message   : {'correctly rejected' if not key.verify(wrong_msg, sig) else 'BUG'}"
    )
    assert not key.verify(wrong_msg, sig)

    # --- Eve tries 1000 random forgeries ---
    eve_rng = random.Random(999)
    n = o + v
    successes = sum(
        key.verify(msg, [eve_rng.randrange(q) for _ in range(n)]) for _ in range(1000)
    )
    print(f"Eve's forgeries : {successes}/1000 accepted  (expect 0)")
    assert successes == 0
    print()
    print("All checks passed.")


if __name__ == "__main__":
    main()
