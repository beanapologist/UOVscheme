"""UOVKey: public-key evaluation, signing, and verification."""

import random
from dataclasses import dataclass
from typing import List, Optional
from .central_map import CentralMap
from .field import mat_mul_vec, gauss_solve


@dataclass
class UOVKey:
    """A UOV key pair.

    Secret key: (F, T, T_inv)
    Public key: P(σ) = F(T·σ) — composed map, oil subspace hidden.
    """

    q: int
    o: int
    v: int
    F: CentralMap
    T: List[List[int]]  # (o+v)×(o+v), invertible
    T_inv: List[List[int]]  # precomputed inverse of T

    def public_eval(self, sigma: List[int]) -> List[int]:
        """P(σ) = F(oilPart(T·σ), vinPart(T·σ))."""
        x = mat_mul_vec(self.T, sigma, self.q)
        oil = x[: self.o]
        vin = x[self.o :]
        return self.F.eval(oil, vin)

    def sign(
        self, y: List[int], rng: random.Random, max_attempts: int = 1000
    ) -> Optional[List[int]]:
        """Sign message y ∈ GF(q)^o.

        Chooses random vinegar vin, forms the linear system M(vin)·oil = y − b(vin),
        solves by Gaussian elimination, retries if M is singular.
        Returns T^{-1}·(oil ++ vin), or None if max_attempts exceeded.
        """
        for _ in range(max_attempts):
            vin = [rng.randrange(self.q) for _ in range(self.v)]
            M = self.F.lin_matrix(vin)
            b = self.F.vin_const_vec(vin)
            rhs = [(y[i] - b[i]) % self.q for i in range(self.o)]
            oil = gauss_solve(M, rhs, self.q)
            if oil is None:
                continue
            combined = oil + vin
            sigma = mat_mul_vec(self.T_inv, combined, self.q)
            return sigma
        return None

    def verify(self, y: List[int], sigma: List[int]) -> bool:
        """Check that P(σ) = y."""
        return self.public_eval(sigma) == y
