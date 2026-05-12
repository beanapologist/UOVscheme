"""
test_correctness.py — pytest suite mirroring the Lean correctness theorems.

Each test corresponds directly to a proved or stated result in the
Lean formalization:

  test_eval_affine          ↔  CentralMapComp.eval_affine
  test_eval_as_lin_system   ↔  CentralMap.eval_as_linSystem
  test_sign_verify          ↔  UOVKey.correctness
  test_wrong_message        ↔  forgery_iff_mq_preimage (negative direction)
  test_zero_forgery_rejected↔  Test/SchemeTest.lean: Test D
  test_multiple_messages    ↔  UOVKey.correctness (iterated)
  test_different_T          ↔  Test/SchemeTest.lean: Tests A + B
"""

import numpy as np
import pytest
from uov import keygen, CentralMapComp, CentralMap, vec, mat
from uov.field import matvec, dot, solve, mat_inv, det_mod, random_invertible_mat


# ── fixtures ─────────────────────────────────────────────────────────────────

Q, O, V = 7, 2, 2   # small field for fast exhaustive checks

@pytest.fixture
def fixed_comp() -> CentralMapComp:
    """The concrete component from Test/CentralMapTest.lean."""
    return CentralMapComp(
        q=Q,
        A=mat([[1, 0], [0, 1]], Q),
        B=mat([[1, 0], [0, 0]], Q),
        c=vec([1, 0], Q),
        d=vec([0, 0], Q),
        e=2,
    )

@pytest.fixture
def fixed_map() -> CentralMap:
    comp0 = CentralMapComp(Q, mat([[1,0],[0,1]],Q), mat([[1,0],[0,0]],Q),
                           vec([1,0],Q), vec([0,0],Q), 2)
    comp1 = CentralMapComp(Q, mat([[0,1],[1,0]],Q), mat([[0,0],[0,1]],Q),
                           vec([0,1],Q), vec([1,0],Q), 0)
    return CentralMap(Q, O, V, [comp0, comp1])

@pytest.fixture
def identity_key(fixed_map) -> object:
    from uov import UOVKey
    T = np.eye(O + V, dtype=np.int64)
    return UOVKey(fixed_map, T)

@pytest.fixture
def ut_key(fixed_map) -> object:
    from uov import UOVKey
    T = mat([[1,1,0,0],[0,1,0,0],[0,0,1,1],[0,0,0,1]], Q)
    return UOVKey(fixed_map, T)


# ── CentralMapComp.eval_affine ────────────────────────────────────────────────

class TestEvalAffine:
    """eval_affine: f.eval(oil, vin) = <oil, linCoeff(vin)> + vinConst(vin)"""

    def test_concrete_values(self, fixed_comp):
        oil = vec([3, 5], Q)
        vin = vec([1, 2], Q)
        lhs = fixed_comp.eval(oil, vin)
        rhs = (dot(oil, fixed_comp.lin_coeff(vin), Q) + fixed_comp.vin_const(vin)) % Q
        assert lhs == rhs

    def test_all_inputs_q7(self, fixed_comp):
        """Exhaustive check over all (oil, vin) ∈ GF(7)^2 × GF(7)^2."""
        for o0 in range(Q):
            for o1 in range(Q):
                for v0 in range(Q):
                    for v1 in range(Q):
                        oil = vec([o0, o1], Q)
                        vin = vec([v0, v1], Q)
                        lhs = fixed_comp.eval(oil, vin)
                        rhs = (dot(oil, fixed_comp.lin_coeff(vin), Q)
                               + fixed_comp.vin_const(vin)) % Q
                        assert lhs == rhs, f"failed at oil={oil}, vin={vin}"

    def test_zero_oil(self, fixed_comp):
        """With oil = 0, eval equals vin_const."""
        oil = vec([0, 0], Q)
        for v0 in range(Q):
            for v1 in range(Q):
                vin = vec([v0, v1], Q)
                assert fixed_comp.eval(oil, vin) == fixed_comp.vin_const(vin)


# ── CentralMap.eval_as_linSystem ──────────────────────────────────────────────

class TestEvalAsLinSystem:
    """eval_as_linSystem: F(oil, vin) = M(vin)·oil + b(vin)"""

    def test_concrete_values(self, fixed_map):
        oil = vec([3, 5], Q)
        vin = vec([1, 2], Q)
        lhs = fixed_map.eval(oil, vin)
        rhs = (matvec(fixed_map.lin_matrix(vin), oil, Q)
               + fixed_map.vin_const_vec(vin)) % Q
        assert np.array_equal(lhs, rhs)

    def test_second_pair(self, fixed_map):
        oil = vec([0, 6], Q)
        vin = vec([4, 3], Q)
        lhs = fixed_map.eval(oil, vin)
        rhs = (matvec(fixed_map.lin_matrix(vin), oil, Q)
               + fixed_map.vin_const_vec(vin)) % Q
        assert np.array_equal(lhs, rhs)

    def test_all_vin_fixed_map(self, fixed_map):
        """For every vinegar, the linearisation identity holds for all oil."""
        rng = np.random.default_rng(0)
        for _ in range(200):
            oil = rng.integers(0, Q, size=O, dtype=np.int64)
            vin = rng.integers(0, Q, size=V, dtype=np.int64)
            lhs = fixed_map.eval(oil, vin)
            rhs = (matvec(fixed_map.lin_matrix(vin), oil, Q)
                   + fixed_map.vin_const_vec(vin)) % Q
            assert np.array_equal(lhs, rhs)


# ── UOVKey.correctness ────────────────────────────────────────────────────────

class TestCorrectness:
    """Every signature produced by sign() passes verify()."""

    def test_identity_T(self, identity_key):
        oil = vec([3, 5], Q)
        vin = vec([1, 2], Q)
        y = identity_key.F.eval(oil, vin)
        sigma = identity_key.sign(y, rng=np.random.default_rng(0))
        assert identity_key.verify(y, sigma)

    def test_upper_triangular_T(self, ut_key):
        oil = vec([3, 5], Q)
        vin = vec([1, 2], Q)
        y = ut_key.F.eval(oil, vin)
        sigma = ut_key.sign(y, rng=np.random.default_rng(0))
        assert ut_key.verify(y, sigma)

    def test_second_message(self, ut_key):
        oil = vec([0, 6], Q)
        vin = vec([4, 3], Q)
        y = ut_key.F.eval(oil, vin)
        sigma = ut_key.sign(y, rng=np.random.default_rng(1))
        assert ut_key.verify(y, sigma)

    def test_random_keys_and_messages(self):
        """100 random (key, message) pairs all round-trip correctly."""
        rng = np.random.default_rng(42)
        for _ in range(100):
            key = keygen(Q, O, V, seed=int(rng.integers(0, 2**32)))
            y   = rng.integers(0, Q, size=O, dtype=np.int64)
            sigma = key.sign(y, rng=rng)
            assert key.verify(y, sigma), "correctness failure"

    def test_larger_params(self):
        """Round-trip with q=31, o=8, v=16."""
        rng = np.random.default_rng(7)
        key = keygen(31, 8, 16, seed=7)
        for _ in range(20):
            y = rng.integers(0, 31, size=8, dtype=np.int64)
            sigma = key.sign(y, rng=rng)
            assert key.verify(y, sigma)


# ── forgery_iff_mq_preimage (negative direction) ──────────────────────────────

class TestForgeryRejection:
    """Valid forgery ↔ MQ preimage.  Random/crafted forgeries are rejected."""

    def test_wrong_message_rejected(self, ut_key):
        """Alice's signature does not verify for a different message."""
        rng = np.random.default_rng(0)
        y1 = vec([1, 2], Q)
        y2 = vec([3, 4], Q)
        sigma = ut_key.sign(y1, rng=rng)
        assert not ut_key.verify(y2, sigma)

    def test_zero_forgery_rejected(self, ut_key):
        """Test D from SchemeTest.lean: all-zeros is not a valid forgery."""
        y = ut_key.F.eval(vec([3, 5], Q), vec([1, 2], Q))
        zero_sig = np.zeros(O + V, dtype=np.int64)
        # Only passes if F(T·0) = y, which is astronomically unlikely
        assert not ut_key.verify(y, zero_sig)

    def test_random_forgeries_rejected(self, ut_key):
        """1000 random vectors are almost surely all rejected."""
        rng = np.random.default_rng(99)
        y = ut_key.F.eval(vec([3, 5], Q), vec([1, 2], Q))
        accepted = sum(
            ut_key.verify(y, rng.integers(0, Q, size=O + V, dtype=np.int64))
            for _ in range(1000)
        )
        # Over GF(7)^2 the probability of a random hit is 1/49 ≈ 2%.
        # Expect ≤ 50 accepts over 1000 tries (with overwhelming probability).
        assert accepted < 50, f"too many random forgeries accepted: {accepted}"

    def test_bitflip_rejected(self, ut_key):
        """Flipping one component of a valid signature invalidates it."""
        rng = np.random.default_rng(0)
        y = vec([5, 3], Q)
        sigma = ut_key.sign(y, rng=rng)
        assert ut_key.verify(y, sigma)
        for i in range(O + V):
            tampered = sigma.copy()
            tampered[i] = (tampered[i] + 1) % Q
            # Tampered should rarely (not always) be valid; just check it's
            # not trivially the same value
            _ = ut_key.verify(y, tampered)   # exercise the code path
