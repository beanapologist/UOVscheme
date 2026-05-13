"""Field element RNG: CSPRNG default, injectable for deterministic tests."""

from __future__ import annotations

import random
import secrets
from typing import Protocol, runtime_checkable


@runtime_checkable
class FieldRng(Protocol):
    """Uniform integers in [0, n) for field sampling."""

    def randbelow(self, n: int) -> int:
        ...


class SecretsRng:
    """OS-backed CSPRNG (secrets module)."""

    def randbelow(self, n: int) -> int:
        if n <= 0:
            raise ValueError("randbelow requires n > 0")
        return secrets.randbelow(n)


class RandomAdapter:
    """Wraps ``random.Random`` for reproducible tests only — not for production."""

    def __init__(self, r: random.Random) -> None:
        self._r = r

    def randbelow(self, n: int) -> int:
        if n <= 0:
            raise ValueError("randbelow requires n > 0")
        return self._r.randrange(n)
