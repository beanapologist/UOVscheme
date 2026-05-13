"""Tests for silentverify.state_cert/v1 wire format and pipeline."""

import os
import random
import sys
import warnings

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from uov import RandomAdapter, keygen
from uov.certificate import (
    SCHEMA_LEGACY_EIGENVERSE,
    SCHEMA_LEGACY_FIELDCERT,
    SCHEMA_V1,
    StateCertificateV1,
    b64decode_canonical,
    b64encode_canonical,
    issue_message_certificate,
    message_matches_certificate,
    public_key_wire,
    uovkey_from_public_wire,
    verify_certificate,
)


def det_rng(seed: int) -> RandomAdapter:
    return RandomAdapter(random.Random(seed))


def test_issue_verify_roundtrip_json():
    rng = det_rng(1)
    with warnings.catch_warnings():
        warnings.simplefilter("ignore", UserWarning)
        key = keygen(31, 4, 8, rng=rng, allow_toy_params=True)
    msg = b"state commitment bytes"
    cert = issue_message_certificate(key, msg, rng=rng)
    assert cert.schema_version == SCHEMA_V1
    assert verify_certificate(cert)
    js = cert.to_json(indent=None)
    cert2 = StateCertificateV1.from_json(js)
    assert verify_certificate(cert2)
    assert message_matches_certificate(cert2, msg)


def test_public_key_roundtrip():
    rng = det_rng(2)
    with warnings.catch_warnings():
        warnings.simplefilter("ignore", UserWarning)
        key = keygen(31, 4, 8, rng=rng, allow_toy_params=True)
    w = public_key_wire(key)
    vk = uovkey_from_public_wire(w)
    y = [rng.randbelow(31) for _ in range(4)]
    sig = key.sign(y, rng)
    assert sig is not None
    assert vk.verify(y, sig)


def test_verify_rejects_tampered_sigma():
    rng = det_rng(3)
    with warnings.catch_warnings():
        warnings.simplefilter("ignore", UserWarning)
        key = keygen(31, 4, 8, rng=rng, allow_toy_params=True)
    cert = issue_message_certificate(key, b"x", rng=rng)
    cert.sigma = [(cert.sigma[0] + 1) % 31] + cert.sigma[1:]
    assert not verify_certificate(cert)


def test_from_json_rejects_bad_schema():
    import pytest

    bad = (
        '{"schema_version": "other/v0", "q": 31, "o": 4, "v": 8, '
        '"digest_y": [0,0,0,0], "sigma": [0,0,0,0,0,0,0,0,0,0,0,0], '
        '"public_key": {"q":31,"o":4,"v":8,"central_map":{"comps":[]},"T":[]}}'
    )
    with pytest.raises(ValueError, match="unsupported"):
        StateCertificateV1.from_json(bad)


def test_legacy_eigenverse_schema_loads():
    rng = det_rng(99)
    with warnings.catch_warnings():
        warnings.simplefilter("ignore", UserWarning)
        key = keygen(31, 4, 8, rng=rng, allow_toy_params=True)
    cert = issue_message_certificate(key, b"z", rng=rng)
    d = cert.to_wire_dict()
    d["schema_version"] = SCHEMA_LEGACY_EIGENVERSE
    c2 = StateCertificateV1.from_wire_dict(d)
    assert c2.schema_version == SCHEMA_V1
    assert verify_certificate(c2)


def test_legacy_fieldcert_schema_loads():
    rng = det_rng(98)
    with warnings.catch_warnings():
        warnings.simplefilter("ignore", UserWarning)
        key = keygen(31, 4, 8, rng=rng, allow_toy_params=True)
    cert = issue_message_certificate(key, b"w", rng=rng)
    d = cert.to_wire_dict()
    d["schema_version"] = SCHEMA_LEGACY_FIELDCERT
    c2 = StateCertificateV1.from_wire_dict(d)
    assert c2.schema_version == SCHEMA_V1
    assert verify_certificate(c2)


def test_b64_canonical_roundtrip():
    rng = det_rng(4)
    with warnings.catch_warnings():
        warnings.simplefilter("ignore", UserWarning)
        key = keygen(31, 4, 8, rng=rng, allow_toy_params=True)
    cert = issue_message_certificate(key, b"y", rng=rng)
    token = b64encode_canonical(cert.to_wire_dict())
    d = b64decode_canonical(token)
    cert2 = StateCertificateV1.from_wire_dict(d)
    assert verify_certificate(cert2)
