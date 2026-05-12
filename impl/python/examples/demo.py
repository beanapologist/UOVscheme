"""
demo.py — Alice signs a message; Bob verifies it; Eve tries to forge.

Run:  python examples/demo.py
"""

import sys
import hashlib
import numpy as np

sys.path.insert(0, __file__.rsplit("/examples", 1)[0])
from uov import keygen
from uov.field import vec


# ── parameters ───────────────────────────────────────────────────────────────
# Small but non-trivial: GF(31) with 6 oil vars and 12 vinegar vars.
# Real security requires much larger parameters (e.g. q=256, o=32, v=64).

Q  = 31    # prime field
O  = 6     # oil variables  (= number of equations = signature output dimension)
V  = 12    # vinegar variables  (≥ O for security margin)

SEED = 42  # reproducible demo


def hash_message(msg: str, o: int, q: int) -> np.ndarray:
    """Hash a message string to a vector in GF(q)^o."""
    digest = hashlib.sha256(msg.encode()).digest()
    return np.array([b % q for b in digest[:o]], dtype=np.int64)


def banner(title: str) -> None:
    print(f"\n{'─'*60}")
    print(f"  {title}")
    print(f"{'─'*60}")


def main() -> None:
    rng = np.random.default_rng(SEED)

    # ── Key generation (Alice) ────────────────────────────────────────────────
    banner("Key generation  (Alice)")
    key = keygen(Q, O, V, seed=SEED)
    print(f"  Field:    GF({Q})")
    print(f"  Oil vars: {O}   Vinegar vars: {V}")
    print(f"  T shape:  {key.T.shape}   (secret transform)")
    print(f"  Public key: F∘T  ({O} quadratic polynomials in {O+V} unknowns)")

    # ── Signing (Alice) ───────────────────────────────────────────────────────
    banner("Signing  (Alice → Bob)")
    message = "Hello, Bob. Transfer 100 coins to Charlie."
    y = hash_message(message, O, Q)
    print(f"  Message:  \"{message}\"")
    print(f"  Hash y:   {y.tolist()}")

    sigma = key.sign(y, rng=rng)
    print(f"  Signature σ: {sigma.tolist()}")

    # ── Verification (Bob) ────────────────────────────────────────────────────
    banner("Verification  (Bob)")
    result = key.verify(y, sigma)
    print(f"  P(σ) = y?  →  {'✓ ACCEPT' if result else '✗ REJECT'}")
    assert result, "correctness failure — this should never happen"

    # ── Forgery attempt (Eve) ─────────────────────────────────────────────────
    banner("Forgery attempt  (Eve)")
    print("  Eve only has the public map P = F∘T.")
    print("  She tries three strategies:\n")

    forged_message = "Hello, Bob. Transfer 100 coins to Eve."
    y_eve = hash_message(forged_message, O, Q)

    # Strategy 1: random guess
    guess1 = rng.integers(0, Q, size=O + V, dtype=np.int64)
    r1 = key.verify(y_eve, guess1)
    print(f"  1. Random σ:       {'✓ accept' if r1 else '✗ reject'}")

    # Strategy 2: reuse Alice's signature for a different hash
    r2 = key.verify(y_eve, sigma)
    print(f"  2. Reuse Alice's σ: {'✓ accept' if r2 else '✗ reject'}")

    # Strategy 3: zero vector
    zero = np.zeros(O + V, dtype=np.int64)
    r3 = key.verify(y_eve, zero)
    print(f"  3. Zero vector:     {'✓ accept' if r3 else '✗ reject'}")

    print("\n  Eve cannot forge without solving the MQ problem.")

    # ── Summary ───────────────────────────────────────────────────────────────
    banner("Summary")
    print("  Alice can sign in O(o²·v) time (linear system solve).")
    print("  Bob verifies in O(o·(o+v)²) time (evaluate o quadratics).")
    print("  Eve must invert P — a random system of o quadratics in o+v")
    print("  unknowns over GF(q).  No polynomial-time algorithm is known.")


if __name__ == "__main__":
    main()
