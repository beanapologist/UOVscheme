#!/usr/bin/env python3
"""SilentVerify end-to-end demo: CRT bridge → chain state digest → UOV certificate → verify.

Run from ``impl/python``::

    python demos/silentverify_demo.py
"""

from __future__ import annotations

import json
import random
import sys
from pathlib import Path

_root = Path(__file__).resolve().parent.parent
if str(_root) not in sys.path:
    sys.path.insert(0, str(_root))

from uov import RandomAdapter, keygen  # noqa: E402
from uov.params import NIST_STYLE_PRIME_I_MIN  # noqa: E402
from statecert import (  # noqa: E402
    CRTBridge,
    ChainState,
    CrossChainStateTransition,
    StateVerifier,
)


def _hr(title: str) -> None:
    print()
    print("═" * 72)
    print(f"  {title}")
    print("═" * 72)


def main() -> None:
    rng = RandomAdapter(random.Random(2026))

    _hr("1. CRT bridge (Python mirror of CRTBridge.lean)")
    br = CRTBridge(7, 11)
    secret = 42
    pair = br.encode(secret)
    print(f"  Encode a = {secret} mod {br.mn}  →  (a mod 7, a mod 11) = {pair}")
    print(f"  Decode back  →  {br.decode(*pair)}  (expect {secret % br.mn})")

    _hr("2. UOV key (NIST-style prime-field profile; see uov.params docstring)")
    q, o, v = NIST_STYLE_PRIME_I_MIN
    key = keygen(q, o, v, rng=rng, allow_toy_params=False)
    print(f"  Field GF({key.q}), oil={key.o}, vinegar={key.v}")

    _hr("3. ChainState → digest y ∈ GF(q)^o  (SHA-256 → field expansion)")
    eth = ChainState("eip155:11155111", 19_000_000, "0xdeadbeef")
    verifier = StateVerifier(key)
    y = verifier.digest_for_chain_state(eth)
    print(f"  State: {json.dumps(eth.to_canonical_dict())}")
    print(f"  Digest y (first two coords): {y[:2]} … (length {len(y)})")

    _hr("4. Issue certificate + verify (stateless P(σ) = y)")
    cert = verifier.issue_for_chain_state(eth, rng, metadata={"demo": "silentverify"})
    ok = StateVerifier.verify_certificate(cert)
    print(f"  pubkey_fp: {cert.pubkey_fp[:16]}…")
    print(f"  verify(): {ok}")
    wire = cert.to_json(indent=None)
    print(f"  JSON size: {len(wire)} bytes")

    _hr("5. Cross-chain digest (two EVM chains, toy state roots)")
    poly = ChainState("eip155:137", 12_000_000, "0xcafe")
    x = CrossChainStateTransition(eth, poly)
    y2 = verifier.digest_for_cross_chain(x)
    cert2 = verifier.issue_for_cross_chain(x, rng, metadata={"pair": "eth-sol"})
    print(f"  verify cross-chain cert: {StateVerifier.verify_certificate(cert2)}")
    print(f"  Single-chain digest vs cross-chain digest equal? {y == y2}  (different payloads)")

    _hr("6. Tamper check")
    cert_bad = verifier.issue_for_chain_state(eth, RandomAdapter(random.Random(123)))
    cert_bad.inner.sigma = [(cert_bad.inner.sigma[0] + 1) % key.q] + cert_bad.inner.sigma[1:]
    print(f"  After flipping one σ coordinate: {StateVerifier.verify_certificate(cert_bad)}")

    _hr("Done")
    print("  For cryptographic UOV Alice/Bob/Eve, see:  python examples/demo.py")
    print()


if __name__ == "__main__":
    main()
