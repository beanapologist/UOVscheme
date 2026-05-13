"""CentralMapComp and CentralMap — Python mirror of CentralMap.lean."""

from __future__ import annotations

from dataclasses import dataclass
from typing import List

from .field import dot, mat_mul_vec, random_matrix, random_vec
from .rng import FieldRng


@dataclass
class CentralMapComp:
    """One UOV polynomial: F_k(oil, vin) = oil·A·vin + vin·B·vin + c·oil + d·vin + e.

    The oil×oil block is absent by construction.
    """

    q: int
    o: int
    v: int
    A: List[List[int]]  # o×v
    B: List[List[int]]  # v×v
    c: List[int]  # length o
    d: List[int]  # length v
    e: int

    def eval(self, oil: List[int], vin: List[int]) -> int:
        """F_k(oil, vin)."""
        Avin = mat_mul_vec(self.A, vin, self.q)
        Bvin = mat_mul_vec(self.B, vin, self.q)
        return (
            dot(oil, Avin, self.q)
            + dot(vin, Bvin, self.q)
            + dot(self.c, oil, self.q)
            + dot(self.d, vin, self.q)
            + self.e
        ) % self.q

    def lin_coeff(self, vin: List[int]) -> List[int]:
        """A·vin + c  (the oil-linear coefficient vector for fixed vin)."""
        Avin = mat_mul_vec(self.A, vin, self.q)
        return [(Avin[i] + self.c[i]) % self.q for i in range(self.o)]

    def vin_const(self, vin: List[int]) -> int:
        """Constant term w.r.t. oil: vin·B·vin + d·vin + e."""
        Bvin = mat_mul_vec(self.B, vin, self.q)
        return (dot(vin, Bvin, self.q) + dot(self.d, vin, self.q) + self.e) % self.q

    @staticmethod
    def random(q: int, o: int, v: int, rng: FieldRng) -> "CentralMapComp":
        return CentralMapComp(
            q=q,
            o=o,
            v=v,
            A=random_matrix(o, v, q, rng),
            B=random_matrix(v, v, q, rng),
            c=random_vec(o, q, rng),
            d=random_vec(v, q, rng),
            e=rng.randbelow(q),
        )


@dataclass
class CentralMap:
    """The full UOV central map: o polynomial components over (o+v) variables."""

    q: int
    o: int
    v: int
    comps: List[CentralMapComp]

    def eval(self, oil: List[int], vin: List[int]) -> List[int]:
        """F(oil, vin) ∈ GF(q)^o."""
        return [comp.eval(oil, vin) for comp in self.comps]

    def lin_matrix(self, vin: List[int]) -> List[List[int]]:
        """o×o matrix M(vin): row k = linCoeff of comp k."""
        return [comp.lin_coeff(vin) for comp in self.comps]

    def vin_const_vec(self, vin: List[int]) -> List[int]:
        """o-vector b(vin): entry k = vinConst of comp k."""
        return [comp.vin_const(vin) for comp in self.comps]

    @staticmethod
    def random(q: int, o: int, v: int, rng: FieldRng) -> "CentralMap":
        return CentralMap(
            q=q,
            o=o,
            v=v,
            comps=[CentralMapComp.random(q, o, v, rng) for _ in range(o)],
        )
