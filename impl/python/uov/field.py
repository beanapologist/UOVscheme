"""
field.py — GF(q) arithmetic for prime fields.

Mirrors the ZMod q infrastructure in the Lean formalization.
All arithmetic is done with plain Python ints; numpy arrays are used for
vectors and matrices but all entries stay in {0, …, q-1}.
"""

import numpy as np
from typing import Optional


# ── scalar helpers ──────────────────────────────────────────────────────────

def inv_mod(a: int, q: int) -> int:
    """Modular inverse of a in GF(q) (q prime). Raises if a ≡ 0."""
    a = int(a) % q
    if a == 0:
        raise ZeroDivisionError("0 has no inverse in GF(q)")
    return pow(a, q - 2, q)


# ── vector / matrix helpers ─────────────────────────────────────────────────

def vec(entries, q: int) -> np.ndarray:
    """Create a GF(q) column vector from a list/array."""
    return np.array(entries, dtype=np.int64) % q


def mat(rows, q: int) -> np.ndarray:
    """Create a GF(q) matrix from a nested list/array."""
    return np.array(rows, dtype=np.int64) % q


def matvec(A: np.ndarray, v: np.ndarray, q: int) -> np.ndarray:
    return A @ v % q


def matmul(A: np.ndarray, B: np.ndarray, q: int) -> np.ndarray:
    return A @ B % q


def dot(u: np.ndarray, v: np.ndarray, q: int) -> int:
    return int(np.dot(u.astype(np.int64), v.astype(np.int64))) % q


# ── Gaussian elimination over GF(q) ─────────────────────────────────────────

def solve(A: np.ndarray, b: np.ndarray, q: int) -> Optional[np.ndarray]:
    """
    Solve A·x = b over GF(q) by Gaussian elimination.

    Returns x as an ndarray if a unique solution exists, None otherwise.
    Corresponds to the linear-system step in UOVKey.sign:
        M(vin) · oil = y − b(vin)
    """
    n = len(b)
    # Augmented matrix [A | b]
    M = np.hstack([A.copy().astype(np.int64), b.reshape(-1, 1).astype(np.int64)]) % q

    for col in range(n):
        # Find pivot
        pivot = None
        for row in range(col, n):
            if M[row, col] % q != 0:
                pivot = row
                break
        if pivot is None:
            return None  # singular — retry with new vinegar

        if pivot != col:
            M[[col, pivot]] = M[[pivot, col]]

        inv = inv_mod(int(M[col, col]), q)
        M[col] = M[col] * inv % q

        for row in range(n):
            if row != col and M[row, col] % q != 0:
                M[row] = (M[row] - M[row, col] * M[col]) % q

    return M[:, n] % q


def mat_inv(A: np.ndarray, q: int) -> Optional[np.ndarray]:
    """
    Matrix inverse over GF(q) via Gauss-Jordan elimination.
    Returns None if A is singular.
    """
    n = A.shape[0]
    aug = np.hstack([A.copy().astype(np.int64), np.eye(n, dtype=np.int64)]) % q

    for col in range(n):
        pivot = None
        for row in range(col, n):
            if aug[row, col] % q != 0:
                pivot = row
                break
        if pivot is None:
            return None

        if pivot != col:
            aug[[col, pivot]] = aug[[pivot, col]]

        inv = inv_mod(int(aug[col, col]), q)
        aug[col] = aug[col] * inv % q

        for row in range(n):
            if row != col and aug[row, col] % q != 0:
                aug[row] = (aug[row] - aug[row, col] * aug[col]) % q

    return aug[:, n:] % q


def det_mod(A: np.ndarray, q: int) -> int:
    """Determinant of A over GF(q)."""
    n = A.shape[0]
    M = A.copy().astype(np.int64) % q
    det = 1
    for col in range(n):
        pivot = None
        for row in range(col, n):
            if M[row, col] % q != 0:
                pivot = row
                break
        if pivot is None:
            return 0
        if pivot != col:
            M[[col, pivot]] = M[[pivot, col]]
            det = (-det) % q
        inv = inv_mod(int(M[col, col]), q)
        det = det * M[col, col] % q
        M[col] = M[col] * inv % q
        for row in range(col + 1, n):
            if M[row, col] % q != 0:
                M[row] = (M[row] - M[row, col] * M[col]) % q
    return int(det) % q


# ── random generation ────────────────────────────────────────────────────────

def random_vec(n: int, q: int, rng=None) -> np.ndarray:
    rng = rng or np.random.default_rng()
    return rng.integers(0, q, size=n, dtype=np.int64)


def random_mat(rows: int, cols: int, q: int, rng=None) -> np.ndarray:
    rng = rng or np.random.default_rng()
    return rng.integers(0, q, size=(rows, cols), dtype=np.int64)


def random_invertible_mat(n: int, q: int, rng=None) -> np.ndarray:
    """Return a random invertible n×n matrix over GF(q)."""
    rng = rng or np.random.default_rng()
    while True:
        A = random_mat(n, n, q, rng)
        if det_mod(A, q) != 0:
            return A
