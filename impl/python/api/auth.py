"""API key validation, SQLite usage quotas, Stripe provisioning."""

from __future__ import annotations

import hashlib
import os
import secrets
import sqlite3
import threading
from contextlib import contextmanager
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, Iterator, Optional

DEFAULT_FREE_MONTHLY = 100
DEFAULT_DB = Path(__file__).resolve().parent.parent / "data" / "silentverify_usage.db"

_lock = threading.Lock()
# Same-process fallback when SQLite path differs or is briefly unavailable (single replica).
_runtime_keys: Dict[str, tuple[str, int]] = {}


def _is_production() -> bool:
    return os.environ.get("SILENTVERIFY_ENV", "").lower() in ("production", "prod")


def _month_key() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m")


def normalize_api_key(raw: Optional[str]) -> str:
    """Strip whitespace, BOM, and common paste mistakes (Bearer / header prefix)."""
    if not raw:
        return ""
    key = raw.strip().strip("\ufeff")
    if key.lower().startswith("bearer "):
        key = key[7:].strip()
    for prefix in ("x-api-key:", "x-api-key ", "api-key:", "apikey:"):
        if key.lower().startswith(prefix):
            key = key[len(prefix) :].strip()
            break
    if len(key) >= 2 and key[0] == key[-1] and key[0] in "\"'":
        key = key[1:-1].strip()
    return key


def _hash_key(api_key: str) -> str:
    return hashlib.sha256(normalize_api_key(api_key).encode("utf-8")).hexdigest()


def _db_path() -> Path:
    raw = os.environ.get("SILENTVERIFY_USAGE_DB", "").strip()
    if raw:
        return Path(raw)
    if _is_production():
        for candidate in (
            Path("/app/data/silentverify_usage.db"),
            Path("/data/silentverify_usage.db"),
        ):
            if candidate.parent.is_dir():
                return candidate
    return DEFAULT_DB


def db_is_configured_persistent() -> bool:
    """True when operator set an explicit DB path (e.g. Railway volume)."""
    return bool(os.environ.get("SILENTVERIFY_USAGE_DB", "").strip())


def init_db() -> None:
    path = _db_path()
    path.parent.mkdir(parents=True, exist_ok=True)
    with _connect() as conn:
        conn.execute("PRAGMA journal_mode=WAL")
        conn.executescript(
            """
            CREATE TABLE IF NOT EXISTS api_keys (
                key_hash TEXT PRIMARY KEY,
                tier TEXT NOT NULL DEFAULT 'free',
                monthly_quota INTEGER NOT NULL DEFAULT 100,
                label TEXT,
                stripe_customer_id TEXT
            );
            CREATE TABLE IF NOT EXISTS usage (
                key_hash TEXT NOT NULL,
                month TEXT NOT NULL,
                endpoint TEXT NOT NULL,
                count INTEGER NOT NULL DEFAULT 0,
                PRIMARY KEY (key_hash, month, endpoint)
            );
            CREATE TABLE IF NOT EXISTS checkout_sessions (
                session_id TEXT PRIMARY KEY,
                status TEXT NOT NULL,
                tier TEXT NOT NULL,
                api_key_hash TEXT,
                api_key_plain TEXT,
                revealed INTEGER NOT NULL DEFAULT 0,
                stripe_customer_id TEXT,
                created_at TEXT NOT NULL
            );
            """
        )
        _migrate_schema(conn)
        conn.commit()
        _load_runtime_from_db(conn)
    _sync_env_keys()


def _load_runtime_from_db(conn: sqlite3.Connection) -> None:
    for row in conn.execute("SELECT key_hash, tier, monthly_quota FROM api_keys"):
        _runtime_keys[str(row["key_hash"])] = (str(row["tier"]), int(row["monthly_quota"]))


def _migrate_schema(conn: sqlite3.Connection) -> None:
    """Add columns introduced after first deploy (SQLite has no IF NOT EXISTS for columns)."""
    api_cols = {row[1] for row in conn.execute("PRAGMA table_info(api_keys)")}
    if api_cols and "stripe_customer_id" not in api_cols:
        conn.execute("ALTER TABLE api_keys ADD COLUMN stripe_customer_id TEXT")
    if not conn.execute(
        "SELECT name FROM sqlite_master WHERE type='table' AND name='checkout_sessions'"
    ).fetchone():
        conn.execute(
            """
            CREATE TABLE checkout_sessions (
                session_id TEXT PRIMARY KEY,
                status TEXT NOT NULL,
                tier TEXT NOT NULL,
                api_key_hash TEXT,
                api_key_plain TEXT,
                revealed INTEGER NOT NULL DEFAULT 0,
                stripe_customer_id TEXT,
                created_at TEXT NOT NULL
            )
            """
        )


def _sync_env_keys() -> None:
    bootstrap = os.environ.get("SILENTVERIFY_BOOTSTRAP_API_KEY", "").strip()
    if bootstrap:
        register_api_key(bootstrap, tier="free", label="bootstrap")
    raw = os.environ.get("SILENTVERIFY_API_KEYS", "").strip()
    if not raw:
        if _is_production():
            return
        default = os.environ.get("SILENTVERIFY_DEV_API_KEY", "sv_dev_test_key")
        raw = f"free:{default}"
    with _connect() as conn:
        for part in raw.split(","):
            part = part.strip()
            if not part:
                continue
            if ":" in part:
                tier, key = part.split(":", 1)
                tier = tier.strip() or "free"
                key = key.strip()
            else:
                tier, key = "free", part
            register_api_key(key, tier=tier, label=key[:8] + "…", conn=conn)
        conn.commit()


def _quota_for_tier(tier: str) -> int:
    if tier == "pro":
        return int(os.environ.get("SILENTVERIFY_PRO_MONTHLY_QUOTA", "100000"))
    return DEFAULT_FREE_MONTHLY


@contextmanager
def _connect() -> Iterator[sqlite3.Connection]:
    conn = sqlite3.connect(str(_db_path()), timeout=30.0)
    conn.row_factory = sqlite3.Row
    try:
        yield conn
    finally:
        conn.close()


def register_api_key(
    api_key: str,
    *,
    tier: str = "free",
    label: Optional[str] = None,
    stripe_customer_id: Optional[str] = None,
    conn: Optional[sqlite3.Connection] = None,
) -> str:
    plain = normalize_api_key(api_key)
    if not plain:
        raise ValueError("empty_api_key")
    kh = _hash_key(plain)
    quota = _quota_for_tier(tier)
    _runtime_keys[kh] = (tier, quota)

    def _run(c: sqlite3.Connection) -> None:
        c.execute(
            """
            INSERT INTO api_keys (key_hash, tier, monthly_quota, label, stripe_customer_id)
            VALUES (?, ?, ?, ?, ?)
            ON CONFLICT(key_hash) DO UPDATE SET
                tier=excluded.tier,
                monthly_quota=excluded.monthly_quota,
                label=excluded.label,
                stripe_customer_id=COALESCE(excluded.stripe_customer_id, api_keys.stripe_customer_id)
            """,
            (kh, tier, quota, label or tier, stripe_customer_id),
        )

    try:
        if conn is not None:
            _run(conn)
        else:
            with _connect() as c:
                _run(c)
                c.commit()
    except sqlite3.Error as exc:
        raise RuntimeError(f"api_key_db_write_failed: {exc}") from exc
    return kh


def save_checkout_session(session_id: str, *, tier: str, status: str) -> None:
    now = datetime.now(timezone.utc).isoformat()
    with _connect() as conn:
        conn.execute(
            """
            INSERT INTO checkout_sessions (session_id, status, tier, created_at)
            VALUES (?, ?, ?, ?)
            ON CONFLICT(session_id) DO UPDATE SET status=excluded.status
            """,
            (session_id, status, tier, now),
        )
        conn.commit()


def provision_key_for_checkout(
    session_id: str,
    *,
    tier: str,
    stripe_customer_id: Optional[str] = None,
) -> Optional[str]:
    api_key = f"sv_{tier}_" + secrets.token_urlsafe(24)
    kh = register_api_key(
        api_key, tier=tier, stripe_customer_id=stripe_customer_id, label="stripe"
    )
    with _connect() as conn:
        conn.execute(
            """
            UPDATE checkout_sessions
            SET status='completed', api_key_hash=?, api_key_plain=?, stripe_customer_id=?
            WHERE session_id=?
            """,
            (kh, api_key, stripe_customer_id, session_id),
        )
        conn.commit()
    return api_key


def get_checkout_session(session_id: str) -> Optional[Dict[str, Any]]:
    with _connect() as conn:
        row = conn.execute(
            "SELECT * FROM checkout_sessions WHERE session_id = ?", (session_id,)
        ).fetchone()
    if row is None:
        return None
    return dict(row)


def reveal_checkout_key(session_id: str) -> str:
    with _lock:
        with _connect() as conn:
            row = conn.execute(
                "SELECT api_key_plain, revealed, status FROM checkout_sessions WHERE session_id = ?",
                (session_id,),
            ).fetchone()
            if row is None:
                raise ValueError("unknown_session")
            if row["status"] != "completed" or not row["api_key_plain"]:
                raise ValueError("session_not_ready")
            if int(row["revealed"]):
                raise ValueError("already_revealed")
            key = str(row["api_key_plain"])
            conn.execute(
                "UPDATE checkout_sessions SET revealed=1, api_key_plain=NULL WHERE session_id = ?",
                (session_id,),
            )
            conn.commit()
            return key


def validate_api_key(api_key: Optional[str]) -> tuple[str, str, int]:
    plain = normalize_api_key(api_key)
    if not plain:
        raise ValueError("missing_api_key")
    kh = _hash_key(plain)
    if kh in _runtime_keys:
        tier, quota = _runtime_keys[kh]
        return kh, tier, quota
    try:
        with _connect() as conn:
            row = conn.execute(
                "SELECT tier, monthly_quota FROM api_keys WHERE key_hash = ?", (kh,)
            ).fetchone()
        if row is not None:
            tier, quota = str(row["tier"]), int(row["monthly_quota"])
            _runtime_keys[kh] = (tier, quota)
            return kh, tier, quota
    except sqlite3.Error:
        if kh in _runtime_keys:
            tier, quota = _runtime_keys[kh]
            return kh, tier, quota
        raise
    _sync_env_keys()
    if kh in _runtime_keys:
        tier, quota = _runtime_keys[kh]
        return kh, tier, quota
    try:
        with _connect() as conn:
            row = conn.execute(
                "SELECT tier, monthly_quota FROM api_keys WHERE key_hash = ?", (kh,)
            ).fetchone()
    except sqlite3.Error:
        raise ValueError("invalid_api_key") from None
    if row is None:
        raise ValueError("invalid_api_key")
    tier, quota = str(row["tier"]), int(row["monthly_quota"])
    _runtime_keys[kh] = (tier, quota)
    return kh, tier, quota


def count_registered_keys() -> int:
    try:
        with _connect() as conn:
            row = conn.execute("SELECT COUNT(*) AS n FROM api_keys").fetchone()
        return int(row["n"]) if row else 0
    except sqlite3.Error:
        return len(_runtime_keys)


def auth_diagnostics() -> Dict[str, Any]:
    path = _db_path()
    exists = path.is_file()
    writable = False
    if not exists:
        try:
            path.parent.mkdir(parents=True, exist_ok=True)
            path.touch()
            writable = True
        except OSError:
            writable = False
    else:
        writable = os.access(path, os.W_OK)
    return {
        "production": _is_production(),
        "persistent_db_configured": db_is_configured_persistent(),
        "db_path": str(path),
        "db_exists": exists,
        "db_writable": writable,
        "registered_keys": count_registered_keys(),
        "runtime_keys_cached": len(_runtime_keys),
        "replica_hint": (
            "If registered_keys is 0 after free-key, or keys work intermittently, "
            "set Railway replicas to 1 and mount SILENTVERIFY_USAGE_DB on a volume."
        ),
    }


def invalid_key_hint() -> str:
    if _is_production() and not db_is_configured_persistent():
        return (
            "This key is not registered. Free keys are stored on the server — after a "
            "deploy without a persistent volume, old keys stop working. Get a new key at / "
            "(Get free API key). Operators: set SILENTVERIFY_USAGE_DB on a Railway volume "
            "or SILENTVERIFY_API_KEYS for fixed keys."
        )
    return (
        "Unknown API key. Use the key from Home (Get free API key) or check "
        "SILENTVERIFY_API_KEYS on the server."
    )


def check_and_record_usage(key_hash: str, endpoint: str, monthly_quota: int) -> None:
    month = _month_key()
    with _lock:
        with _connect() as conn:
            row = conn.execute(
                """
                SELECT count FROM usage
                WHERE key_hash = ? AND month = ? AND endpoint = 'issue'
                """,
                (key_hash, month),
            ).fetchone()
            total = int(row["count"]) if row else 0
            if total >= monthly_quota:
                raise ValueError("quota_exceeded")
            conn.execute(
                """
                INSERT INTO usage (key_hash, month, endpoint, count)
                VALUES (?, ?, 'issue', 1)
                ON CONFLICT(key_hash, month, endpoint)
                DO UPDATE SET count = count + 1
                """,
                (key_hash, month),
            )
            conn.commit()


def usage_summary(key_hash: str) -> dict:
    month = _month_key()
    with _connect() as conn:
        row = conn.execute(
            "SELECT count FROM usage WHERE key_hash = ? AND month = ? AND endpoint = 'issue'",
            (key_hash, month),
        ).fetchone()
        key_row = conn.execute(
            "SELECT tier, monthly_quota FROM api_keys WHERE key_hash = ?", (key_hash,)
        ).fetchone()
    used = int(row["count"]) if row else 0
    quota = int(key_row["monthly_quota"]) if key_row else DEFAULT_FREE_MONTHLY
    return {"month": month, "issue_certs_used": used, "issue_certs_quota": quota}
