# Foundry test fixtures

- `state_cert_wire.json` — one-line SilentVerify `StateCertificate` JSON (schema `silentverify.state_cert/v1`) built from a **prime-field NIST-style** UOV profile `(251, 8, 24)` (see `impl/python/uov/params.py`).
- `pubkey_fp.bin` — raw 32-byte SHA-256 fingerprint of the embedded public key JSON.

Regenerate after changing the wire schema or profile::

    python3 impl/python/scripts/gen_foundry_fixture.py

(Run from the repository root.)
