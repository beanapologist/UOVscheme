#!/usr/bin/env python3
"""Alice signs, Bob verifies, Eve fails — NIST-style prime-field profile (see ``uov.params``)."""

import random
import sys

sys.path.insert(0, __file__.rsplit("/", 2)[0])

from uov import RandomAdapter, keygen
from uov.params import NIST_STYLE_PRIME_I_MIN


def main():
    q, o, v = NIST_STYLE_PRIME_I_MIN
    print(f"UOV demo  q={q}  o={o}  v={v}  n={o + v}  (prime-field NIST-style profile)")
    print()

    key = keygen(q, o, v, allow_toy_params=False)
    print("Key generation: OK (OS CSPRNG)")

    sign_rng = RandomAdapter(random.Random(1))
    message = b"hello from Alice"
    sig = key.sign_message(message, rng=sign_rng)
    assert sig is not None, "signing failed"
    print(f"Alice's message : {message!r}")
    print(f"Alice's signature: {sig}")

    ok = key.verify_message(message, sig)
    print(f"Bob verifies    : {'PASS' if ok else 'FAIL'}")
    assert ok

    wrong_msg = b"tampered"
    print(
        f"Wrong message   : {'correctly rejected' if not key.verify_message(wrong_msg, sig) else 'BUG'}"
    )
    assert not key.verify_message(wrong_msg, sig)

    eve_rng = RandomAdapter(random.Random(999))
    n = o + v
    successes = sum(
        key.verify_message(message, [eve_rng.randbelow(q) for _ in range(n)])
        for _ in range(1000)
    )
    print(f"Eve's forgeries : {successes}/1000 accepted  (expect 0)")
    assert successes == 0
    print()
    print("All checks passed.")


if __name__ == "__main__":
    main()
