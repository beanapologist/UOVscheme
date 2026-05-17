"""API key normalization and production registration."""

from api import auth


def test_normalize_strips_bearer_and_quotes():
    assert auth.normalize_api_key('  "sv_free_abc"  ') == "sv_free_abc"
    assert auth.normalize_api_key("Bearer sv_free_xyz") == "sv_free_xyz"
    assert auth.normalize_api_key("X-API-Key: sv_free_q") == "sv_free_q"


def test_production_free_key_roundtrip(tmp_path, monkeypatch):
    monkeypatch.setenv("SILENTVERIFY_ENV", "production")
    monkeypatch.setenv("SILENTVERIFY_USAGE_DB", str(tmp_path / "u.db"))
    auth.init_db()
    key = "sv_free_testkey123456"
    auth.register_api_key(key, tier="free", label="t")
    kh, tier, _ = auth.validate_api_key(key)
    assert tier == "free"
    assert kh == auth._hash_key(key)
