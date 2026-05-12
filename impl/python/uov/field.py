"""GF(q) arithmetic primitives (q prime)."""

import random
from typing import List, Optional


def gf_inv(a: int, q: int) -> int:
    """Modular inverse of a in GF(q) via Fermat's little theorem."""
    if a % q == 0:
        raise ZeroDivisionError("zero has no inverse in GF(q)")
    return pow(int(a), q - 2, q)


def dot(u: List[int], v: List[int], q: int) -> int:
    return sum(x * y for x, y in zip(u, v)) % q


def mat_mul_vec(M: List[List[int]], v: List[int], q: int) -> List[int]:
    return [dot(row, v, q) for row in M]


def mat_add(A: List[List[int]], B: List[List[int]], q: int) -> List[List[int]]:
    return [[(A[i][j] + B[i][j]) % q for j in range(len(A[0]))] for i in range(len(A))]


def mat_mul(A: List[List[int]], B: List[List[int]], q: int) -> List[List[int]]:
    rows, mid, cols = len(A), len(B), len(B[0])
    return [
        [sum(A[i][k] * B[k][j] for k in range(mid)) % q for j in range(cols)]
        for i in range(rows)
    ]


def gauss_solve(M: List[List[int]], b: List[int], q: int) -> Optional[List[int]]:
    """Solve M·x = b over GF(q). Returns None if M is singular."""
    n = len(b)
    # Augmented matrix [M | b]
    aug = [[M[i][j] for j in range(n)] + [b[i]] for i in range(n)]

    for col in range(n):
        # Find pivot
        pivot = None
        for row in range(col, n):
            if aug[row][col] % q != 0:
                pivot = row
                break
        if pivot is None:
            return None
        aug[col], aug[pivot] = aug[pivot], aug[col]

        inv_p = gf_inv(aug[col][col], q)
        for j in range(col, n + 1):
            aug[col][j] = aug[col][j] * inv_p % q

        for row in range(n):
            if row == col:
                continue
            factor = aug[row][col]
            if factor == 0:
                continue
            for j in range(col, n + 1):
                aug[row][j] = (aug[row][j] - factor * aug[col][j]) % q

    return [aug[i][n] for i in range(n)]


def gf_matinv(M: List[List[int]], q: int) -> Optional[List[List[int]]]:
    """Invert an n×n matrix over GF(q). Returns None if singular."""
    n = len(M)
    # Augmented with identity
    aug = [
        [M[i][j] for j in range(n)] + [1 if i == j else 0 for j in range(n)]
        for i in range(n)
    ]

    for col in range(n):
        pivot = None
        for row in range(col, n):
            if aug[row][col] % q != 0:
                pivot = row
                break
        if pivot is None:
            return None
        aug[col], aug[pivot] = aug[pivot], aug[col]

        inv_p = gf_inv(aug[col][col], q)
        for j in range(2 * n):
            aug[col][j] = aug[col][j] * inv_p % q

        for row in range(n):
            if row == col:
                continue
            factor = aug[row][col]
            if factor == 0:
                continue
            for j in range(2 * n):
                aug[row][j] = (aug[row][j] - factor * aug[col][j]) % q

    return [[aug[i][n + j] for j in range(n)] for i in range(n)]


def gf_random_invertible(n: int, q: int, rng: random.Random) -> List[List[int]]:
    """Sample a random invertible n×n matrix over GF(q)."""
    while True:
        M = [[rng.randrange(q) for _ in range(n)] for _ in range(n)]
        if gf_matinv(M, q) is not None:
            return M


def random_matrix(rows: int, cols: int, q: int, rng: random.Random) -> List[List[int]]:
    return [[rng.randrange(q) for _ in range(cols)] for _ in range(rows)]


def random_vec(n: int, q: int, rng: random.Random) -> List[int]:
    return [rng.randrange(q) for _ in range(n)]
