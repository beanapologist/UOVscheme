"""pytest suite — mirrors every Lean theorem in CentralMap.lean and SchemeCorrectness.lean."""

import random
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from uov import keygen
from uov.field import dot, mat_mul_vec, gauss_solve, gf_matinv
from uov.central_map import CentralMapComp, CentralMap


# ── helpers ──────────────────────────────────────────────────────────────────


def make_comp(q, o, v, seed):
    rng = random.Random(seed)
    return CentralMapComp.random(q, o, v, rng)


def make_key(q, o, v, seed=0):
    return keygen(q, o, v, seed=seed)


# ── eval_affine (CentralMapComp.eval_affine in Lean) ─────────────────────────


class TestEvalAffine:
    """eval(oil, vin) == dot(oil, linCoeff(vin)) + vinConst(vin) for all inputs."""

    def test_exhaustive_small(self):
        """Exhaustive check over GF(7)^2 × GF(7)^2 (2401 cases)."""
        q, o, v = 7, 2, 2
        comp = make_comp(q, o, v, seed=0)
        for oil0 in range(q):
            for oil1 in range(q):
                for vin0 in range(q):
                    for vin1 in range(q):
                        oil = [oil0, oil1]
                        vin = [vin0, vin1]
                        lhs = comp.eval(oil, vin)
                        rhs = (
                            dot(oil, comp.lin_coeff(vin), q) + comp.vin_const(vin)
                        ) % q
                        assert lhs == rhs, f"eval_affine failed at oil={oil} vin={vin}"

    def test_random_large(self):
        """100 random checks over GF(31) with o=4, v=8."""
        q, o, v = 31, 4, 8
        rng = random.Random(7)
        comp = make_comp(q, o, v, seed=3)
        for _ in range(100):
            oil = [rng.randrange(q) for _ in range(o)]
            vin = [rng.randrange(q) for _ in range(v)]
            lhs = comp.eval(oil, vin)
            rhs = (dot(oil, comp.lin_coeff(vin), q) + comp.vin_const(vin)) % q
            assert lhs == rhs

    def test_zero_oil(self):
        """At oil=0, eval equals vinConst."""
        q, o, v = 13, 3, 5
        comp = make_comp(q, o, v, seed=1)
        rng = random.Random(2)
        for _ in range(20):
            vin = [rng.randrange(q) for _ in range(v)]
            assert comp.eval([0] * o, vin) == comp.vin_const(vin)

    def test_zero_vin(self):
        """At vin=0, eval equals dot(c, oil) + e."""
        q, o, v = 13, 3, 5
        comp = make_comp(q, o, v, seed=2)
        rng = random.Random(3)
        for _ in range(20):
            oil = [rng.randrange(q) for _ in range(o)]
            expected = (dot(comp.c, oil, q) + comp.e) % q
            assert comp.eval(oil, [0] * v) == expected


# ── eval_as_linSystem (CentralMap.eval_as_linSystem in Lean) ─────────────────


class TestEvalAsLinSystem:
    """F(oil, vin) == M(vin)·oil + b(vin) for the full central map."""

    def test_random(self):
        q, o, v = 31, 4, 6
        rng = random.Random(10)
        F = CentralMap.random(q, o, v, rng)
        for _ in range(50):
            oil = [rng.randrange(q) for _ in range(o)]
            vin = [rng.randrange(q) for _ in range(v)]
            lhs = F.eval(oil, vin)
            M = F.lin_matrix(vin)
            b = F.vin_const_vec(vin)
            rhs = [(mat_mul_vec(M, oil, q)[k] + b[k]) % q for k in range(o)]
            assert lhs == rhs


# ── Gaussian elimination ──────────────────────────────────────────────────────


class TestGaussSolve:
    def test_identity(self):
        q = 17
        n = 4
        identity = [[1 if i == j else 0 for j in range(n)] for i in range(n)]
        b = [3, 1, 4, 1]
        assert gauss_solve(identity, b, q) == b

    def test_random_systems(self):
        q = 31
        rng = random.Random(42)
        for _ in range(50):
            n = rng.randint(2, 6)
            inv_attempt = None
            for _ in range(20):
                M = [[rng.randrange(q) for _ in range(n)] for _ in range(n)]
                inv_attempt = gf_matinv(M, q)
                if inv_attempt is not None:
                    break
            if inv_attempt is None:
                continue
            b = [rng.randrange(q) for _ in range(n)]
            x = gauss_solve(M, b, q)
            assert x is not None
            check = mat_mul_vec(M, x, q)
            assert check == b

    def test_singular_returns_none(self):
        q = 7
        M = [[1, 2], [2, 4]]  # rank 1
        assert gauss_solve(M, [1, 2], q) is None


# ── UOV correctness theorem ───────────────────────────────────────────────────


class TestUOVCorrectness:
    """sign(sk, y) always passes verify(pk, y, ·)."""

    def test_roundtrip_many(self):
        """100 random key/message round trips over GF(31), o=4, v=8."""
        q, o, v = 31, 4, 8
        rng = random.Random(99)
        for i in range(100):
            key = make_key(q, o, v, seed=i)
            msg = [rng.randrange(q) for _ in range(o)]
            sig = key.sign(msg, rng)
            assert sig is not None, f"signing failed on iteration {i}"
            assert key.verify(msg, sig), f"verify failed on iteration {i}"

    def test_wrong_message_rejected(self):
        q, o, v = 31, 4, 8
        rng = random.Random(7)
        key = make_key(q, o, v, seed=5)
        msg = [rng.randrange(q) for _ in range(o)]
        sig = key.sign(msg, rng)
        wrong = [(x + 1) % q for x in msg]
        assert not key.verify(wrong, sig)

    def test_zero_vector_rejected(self):
        q, o, v = 31, 4, 8
        rng = random.Random(8)
        key = make_key(q, o, v, seed=6)
        msg = [rng.randrange(q) for _ in range(o)]
        assert not key.verify(msg, [0] * (o + v))

    def test_forgery_1000(self):
        """1000 random forgeries should all be rejected (astronomically likely)."""
        q, o, v = 31, 4, 8
        rng = random.Random(77)
        key = make_key(q, o, v, seed=7)
        msg = [rng.randrange(q) for _ in range(o)]
        n = o + v
        accepted = sum(
            key.verify(msg, [rng.randrange(q) for _ in range(n)]) for _ in range(1000)
        )
        assert accepted == 0

    def test_different_keys_same_message(self):
        """Signature from key1 must not verify under key2."""
        q, o, v = 31, 4, 8
        rng = random.Random(55)
        key1 = make_key(q, o, v, seed=10)
        key2 = make_key(q, o, v, seed=11)
        msg = [rng.randrange(q) for _ in range(o)]
        sig = key1.sign(msg, rng)
        assert key1.verify(msg, sig)
        assert not key2.verify(msg, sig)

    def test_small_field(self):
        """GF(2) — edge case where almost everything is 0 or 1."""
        q, o, v = 2, 2, 4
        rng = random.Random(0)
        key = make_key(q, o, v, seed=0)
        for msg in [[a, b] for a in range(2) for b in range(2)]:
            sig = key.sign(msg, rng)
            if sig is not None:
                assert key.verify(msg, sig)

    def test_parameters_gf7_o3_v5(self):
        q, o, v = 7, 3, 5
        rng = random.Random(33)
        key = make_key(q, o, v, seed=33)
        for _ in range(30):
            msg = [rng.randrange(q) for _ in range(o)]
            sig = key.sign(msg, rng)
            assert sig is not None
            assert key.verify(msg, sig)

    def test_public_eval_consistent(self):
        """public_eval(sign(oil, vin)) == F.eval(oil, vin) for known oil/vin."""
        q, o, v = 31, 4, 8
        rng = random.Random(1234)
        key = make_key(q, o, v, seed=22)
        oil = [rng.randrange(q) for _ in range(o)]
        vin = [rng.randrange(q) for _ in range(v)]
        y = key.F.eval(oil, vin)

        from uov.field import mat_mul_vec

        combined = oil + vin
        sigma = mat_mul_vec(key.T_inv, combined, q)

        assert key.public_eval(sigma) == y
        assert key.verify(y, sigma)
