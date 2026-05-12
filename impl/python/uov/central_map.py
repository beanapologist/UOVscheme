"""
central_map.py — UOV central map over GF(q).

Direct Python counterpart of UOVscheme/CentralMap.lean.

The central map F : GF(q)^o × GF(q)^v → GF(q)^o consists of o quadratic
polynomials with no oil×oil cross-terms.  Fixing the vinegar variables
reduces F to an affine-linear system in the oil variables (eval_as_linSystem),
which can then be solved by Gaussian elimination.

Lean correspondence
───────────────────
CentralMapComp  ↔  structure CentralMapComp
  .eval          ↔  CentralMapComp.eval
  .lin_coeff     ↔  CentralMapComp.linCoeff
  .vin_const     ↔  CentralMapComp.vinConst

CentralMap      ↔  structure CentralMap
  .eval          ↔  CentralMap.eval
  .lin_matrix    ↔  CentralMap.linMatrix
  .vin_const_vec ↔  CentralMap.vinConstVec
"""

from __future__ import annotations
import numpy as np
from .field import dot, matvec, random_mat, random_vec


class CentralMapComp:
    """
    One polynomial component of the UOV central map.

        F_k(oil, vin) = <oil, A·vin> + <vin, B·vin> + <c, oil> + <d, vin> + e

    The oil×oil block is zero by construction.
    """

    def __init__(
        self,
        q: int,
        A: np.ndarray,   # (o, v)  oil-vinegar cross terms
        B: np.ndarray,   # (v, v)  vinegar-vinegar quadratic
        c: np.ndarray,   # (o,)    linear oil coefficients
        d: np.ndarray,   # (v,)    linear vinegar coefficients
        e: int,          #         constant term
    ):
        self.q = q
        self.A = A % q
        self.B = B % q
        self.c = c % q
        self.d = d % q
        self.e = int(e) % q

    def eval(self, oil: np.ndarray, vin: np.ndarray) -> int:
        """F_k(oil, vin) → element of GF(q)."""
        q = self.q
        return (
            dot(oil, matvec(self.A, vin, q), q)
            + dot(vin, matvec(self.B, vin, q), q)
            + dot(self.c, oil, q)
            + dot(self.d, vin, q)
            + self.e
        ) % q

    def lin_coeff(self, vin: np.ndarray) -> np.ndarray:
        """
        Linear coefficient vector for fixed vinegar: A·vin + c.

        eval(oil, vin) = <oil, lin_coeff(vin)> + vin_const(vin)
        """
        return (matvec(self.A, vin, self.q) + self.c) % self.q

    def vin_const(self, vin: np.ndarray) -> int:
        """Vinegar-only contribution (constant w.r.t. oil)."""
        q = self.q
        return (dot(vin, matvec(self.B, vin, q), q) + dot(self.d, vin, q) + self.e) % q


class CentralMap:
    """
    The full UOV central map: o polynomial components over GF(q)^(o+v).
    """

    def __init__(self, q: int, o: int, v: int, comps: list[CentralMapComp]):
        assert len(comps) == o
        self.q = q
        self.o = o
        self.v = v
        self.comps = comps

    def eval(self, oil: np.ndarray, vin: np.ndarray) -> np.ndarray:
        """F(oil, vin) → vector in GF(q)^o."""
        return np.array([c.eval(oil, vin) for c in self.comps], dtype=np.int64) % self.q

    def lin_matrix(self, vin: np.ndarray) -> np.ndarray:
        """
        o×o linearisation matrix M(vin): row k is lin_coeff of component k.

        eval_as_linSystem: F(oil, vin) = M(vin) · oil + b(vin)
        """
        return np.array([c.lin_coeff(vin) for c in self.comps], dtype=np.int64) % self.q

    def vin_const_vec(self, vin: np.ndarray) -> np.ndarray:
        """Constant vector b(vin): entry k is vin_const of component k."""
        return np.array([c.vin_const(vin) for c in self.comps], dtype=np.int64) % self.q


# ── random key material ──────────────────────────────────────────────────────

def random_central_map(q: int, o: int, v: int, rng=None) -> CentralMap:
    """
    Generate a random UOV central map with o components over GF(q)^(o+v).
    Each component has random A (o×v), B (v×v), c (o), d (v), e.
    """
    rng = rng or np.random.default_rng()
    comps = [
        CentralMapComp(
            q=q,
            A=random_mat(o, v, q, rng),
            B=random_mat(v, v, q, rng),
            c=random_vec(o, q, rng),
            d=random_vec(v, q, rng),
            e=int(rng.integers(0, q)),
        )
        for _ in range(o)
    ]
    return CentralMap(q, o, v, comps)
