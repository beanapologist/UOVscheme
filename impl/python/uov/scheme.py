"""
scheme.py — UOV signature scheme over GF(q).

Direct Python counterpart of UOVscheme/SchemeCorrectness.lean.

Lean correspondence
───────────────────
UOVKey          ↔  structure UOVKey
  .public_eval  ↔  UOVKey.publicEval
  .sign         ↔  UOVKey.sign
  .verify       ↔  UOVKey.verify
  correctness   ↔  UOVKey.correctness  (proved in Lean; tested in tests/)
"""

from __future__ import annotations
import numpy as np
from .central_map import CentralMap
from .field import matvec, mat_inv, solve


class UOVKey:
    """
    A UOV key pair (secret key = F + T; public key = F ∘ T).

    Parameters
    ----------
    F   : CentralMap   — the secret central map
    T   : ndarray      — invertible (o+v)×(o+v) matrix over GF(q)
    """

    def __init__(self, F: CentralMap, T: np.ndarray):
        self.F   = F
        self.q   = F.q
        self.o   = F.o
        self.v   = F.v
        self.T   = T % self.q
        T_inv = mat_inv(T, self.q)
        if T_inv is None:
            raise ValueError("T is singular — det(T) = 0 in GF(q)")
        self.T_inv = T_inv

    # ── helpers ──────────────────────────────────────────────────────────────

    def _oil_part(self, x: np.ndarray) -> np.ndarray:
        """First o components of x  (mirrors UOVKey.oilPart)."""
        return x[: self.o]

    def _vin_part(self, x: np.ndarray) -> np.ndarray:
        """Last v components of x  (mirrors UOVKey.vinPart)."""
        return x[self.o :]

    # ── public map ───────────────────────────────────────────────────────────

    def public_eval(self, sigma: np.ndarray) -> np.ndarray:
        """
        P(σ) = F(T·σ)  — the public map evaluation.

        Mirrors UOVKey.publicEval in SchemeCorrectness.lean.
        """
        x   = matvec(self.T, sigma, self.q)
        oil = self._oil_part(x)
        vin = self._vin_part(x)
        return self.F.eval(oil, vin)

    # ── sign ─────────────────────────────────────────────────────────────────

    def sign(
        self,
        y: np.ndarray,
        rng=None,
        max_retries: int = 128,
    ) -> np.ndarray:
        """
        Sign a message hash y ∈ GF(q)^o.

        Algorithm (mirrors the README / Lean sign function):
          1. Pick random vinegar vin ∈ GF(q)^v.
          2. Form the linear system  M(vin) · oil = y − b(vin).
          3. Solve for oil (Gaussian elimination).  If M(vin) is singular,
             retry with fresh vin — this happens with probability ≤ 1/q.
          4. Return σ = T⁻¹ · (oil ‖ vin).
        """
        rng = rng or np.random.default_rng()
        for _ in range(max_retries):
            vin = rng.integers(0, self.q, size=self.v, dtype=np.int64)
            M   = self.F.lin_matrix(vin)                   # o × o
            b   = self.F.vin_const_vec(vin)                # o
            rhs = (y.astype(np.int64) - b) % self.q        # y − b(vin)

            oil = solve(M, rhs, self.q)
            if oil is not None:
                preimage = np.concatenate([oil, vin])
                return matvec(self.T_inv, preimage, self.q)

        raise RuntimeError(
            f"Signing failed after {max_retries} retries — "
            "increase v or check field parameters"
        )

    # ── verify ───────────────────────────────────────────────────────────────

    def verify(self, y: np.ndarray, sigma: np.ndarray) -> bool:
        """
        Accept σ iff P(σ) = y.

        Mirrors UOVKey.verify in SchemeCorrectness.lean.
        The Lean correctness theorem guarantees that every σ produced by
        sign() passes this check.
        """
        return bool(np.array_equal(self.public_eval(sigma), y % self.q))
