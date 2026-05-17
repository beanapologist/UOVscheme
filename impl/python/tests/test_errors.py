"""Human-readable error hints."""

from api.errors import error_detail, hint_for_message


def test_hint_loopback():
    assert hint_for_message("rpc_url loopback not allowed") is not None


def test_hint_quota_in_detail():
    d = error_detail(error="quota_exceeded", message="quota_exceeded for this key")
    assert d.get("hint") and "quota" in d["hint"].lower()
