#!/usr/bin/env python3
"""Demo: issue a v1 state certificate and verify from JSON (public material only).

For the full SilentVerify pipeline (CRT, chain state, cross-chain), see
``demos/silentverify_demo.py``.
"""

import os
import random
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from uov import RandomAdapter, keygen
from uov.params import NIST_STYLE_PRIME_I_MIN
from uov.certificate import (
    StateCertificateV1,
    b64decode_canonical,
    b64encode_canonical,
    issue_message_certificate,
    message_matches_certificate,
    verify_certificate,
)


def main() -> None:
    rng = RandomAdapter(random.Random(42))
    q, o, v = NIST_STYLE_PRIME_I_MIN
    key = keygen(q, o, v, rng=rng, allow_toy_params=False)

    state = b'{"chain":"demo","height":12345,"root":"0xabc"}\n'
    cert = issue_message_certificate(key, state, rng=rng)

    assert verify_certificate(cert)
    assert message_matches_certificate(cert, state)
    assert not message_matches_certificate(cert, state + b"x")

    js = cert.to_json(indent=None)
    print("Certificate JSON (one line):", js[:120], "...")

    roundtrip = StateCertificateV1.from_json(js)
    assert verify_certificate(roundtrip)

    b64 = b64encode_canonical(roundtrip.to_wire_dict())
    restored = StateCertificateV1.from_wire_dict(b64decode_canonical(b64))
    assert verify_certificate(restored)
    print("Canonical base64 length:", len(b64))
    print("OK: issue → json → verify; base64 round trip OK")


if __name__ == "__main__":
    main()
