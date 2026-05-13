#!/usr/bin/env python3
"""Emit SilentVerify ``StateCertificate`` JSON + ``pubkey_fp`` for Foundry tests.

Writes (relative to repo root)::

    contracts/test/fixtures/state_cert_wire.json   # UTF-8, one-line JSON
    contracts/test/fixtures/pubkey_fp.bin          # raw 32 bytes (SHA-256 of public key JSON)

Uses the same **nist_style_prime** profile as demos (``NIST_STYLE_PRIME_I_MIN``).

Run from repository root::

    python3 impl/python/scripts/gen_foundry_fixture.py
"""

from __future__ import annotations

import random
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(REPO / "impl" / "python"))

from uov import RandomAdapter, keygen  # noqa: E402
from uov.params import NIST_STYLE_PRIME_I_MIN  # noqa: E402
from statecert import ChainState, StateVerifier  # noqa: E402


def main() -> None:
    q, o, v = NIST_STYLE_PRIME_I_MIN
    out_dir = REPO / "contracts" / "test" / "fixtures"
    out_dir.mkdir(parents=True, exist_ok=True)

    rng = RandomAdapter(random.Random(20260213))
    key = keygen(q, o, v, rng=rng, allow_toy_params=False)
    verifier = StateVerifier(key)
    eth = ChainState("eip155:11155111", 5_000_000, "0x" + "aa" * 32)
    cert = verifier.issue_for_chain_state(
        eth, rng, metadata={"fixture": "foundry_anchor"}
    )

    wire_path = out_dir / "state_cert_wire.json"
    wire_path.write_text(cert.to_json(indent=None), encoding="utf-8")

    h = cert.pubkey_fp
    if len(h) != 64:
        raise SystemExit(f"unexpected pubkey_fp length {len(h)}")
    pk_bin = out_dir / "pubkey_fp.bin"
    pk_bin.write_bytes(bytes.fromhex(h))
    print("Wrote", wire_path, "bytes", wire_path.stat().st_size)
    print("Wrote", pk_bin, "bytes", pk_bin.stat().st_size)


if __name__ == "__main__":
    main()
