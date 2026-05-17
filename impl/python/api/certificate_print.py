"""Human-readable printable certificate (HTML)."""

from __future__ import annotations

import html
import json
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional


def _esc(x: Any) -> str:
    return html.escape(str(x)) if x is not None else ""


def _fmt_digest(y: List[int]) -> str:
    if not y:
        return "—"
    return ", ".join(str(i) for i in y[:8]) + ("…" if len(y) > 8 else "")


def render_certificate_html(cert: Dict[str, Any], *, verified: Optional[bool] = None) -> str:
    """Return a print-friendly HTML page for a certificate wire object."""
    meta = cert.get("metadata") or {}
    if not isinstance(meta, dict):
        meta = {}
    agent_did = meta.get("agent_did", "—")
    cert_type = meta.get("cert_type", meta.get("flow", "state"))
    expires = meta.get("expires_at_unix")
    expires_s = (
        datetime.fromtimestamp(int(expires), tz=timezone.utc).strftime("%Y-%m-%d %H:%M UTC")
        if expires is not None
        else "—"
    )
    issued_at = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M UTC")
    pubkey_fp = cert.get("pubkey_fp", "—")
    schema = cert.get("schema_version", "—")
    q, o, v = cert.get("q"), cert.get("o"), cert.get("v")
    verify_badge = ""
    if verified is True:
        verify_badge = '<p class="badge ok">Cryptographic verification: PASSED</p>'
    elif verified is False:
        verify_badge = '<p class="badge fail">Cryptographic verification: FAILED</p>'

    pretty = html.escape(json.dumps(cert, indent=2, sort_keys=True))

    return f"""<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="utf-8" />
  <title>SilentVerify Certificate — {_esc(agent_did if cert_type == 'agent' else cert_type)}</title>
  <link rel="icon" href="/static/silentverify-logo.png" type="image/png" />
  <style>
    :root {{
      --navy: #1a2d4a;
      --cream: #f7f6f3;
      --coral: #d4736f;
      --muted: #5c6b7a;
      --border: #d8dde3;
    }}
    @page {{ margin: 1.2cm; }}
    * {{ box-sizing: border-box; }}
    body {{
      font-family: "DM Sans", Georgia, serif;
      background: var(--cream);
      color: var(--navy);
      margin: 0;
      padding: 24px;
      line-height: 1.5;
    }}
    .sheet {{
      max-width: 720px;
      margin: 0 auto;
      background: #fff;
      border: 2px solid var(--navy);
      border-radius: 12px;
      padding: 32px 36px;
      box-shadow: 0 4px 24px rgba(26,45,74,.08);
    }}
    .head {{
      display: flex;
      align-items: center;
      gap: 16px;
      border-bottom: 2px solid var(--border);
      padding-bottom: 20px;
      margin-bottom: 24px;
    }}
    .head img {{ width: 72px; height: auto; }}
    .head h1 {{
      font-size: 1.5rem;
      margin: 0;
      font-weight: 700;
      letter-spacing: -0.02em;
    }}
    .head p {{ margin: 4px 0 0; color: var(--muted); font-size: 0.9rem; }}
    h2 {{
      font-size: 0.75rem;
      text-transform: uppercase;
      letter-spacing: 0.08em;
      color: var(--coral);
      margin: 20px 0 8px;
    }}
    dl {{
      display: grid;
      grid-template-columns: 140px 1fr;
      gap: 8px 16px;
      margin: 0 0 16px;
      font-size: 0.95rem;
    }}
    dt {{ color: var(--muted); font-weight: 600; }}
    dd {{ margin: 0; word-break: break-all; font-family: "JetBrains Mono", monospace; font-size: 0.85rem; }}
    .badge {{
      display: inline-block;
      padding: 8px 14px;
      border-radius: 8px;
      font-weight: 600;
      font-size: 0.9rem;
    }}
    .badge.ok {{ background: #e8f5ef; color: #1a6b45; }}
    .badge.fail {{ background: #fde8e8; color: #9b2c2c; }}
    pre {{
      background: var(--cream);
      border: 1px solid var(--border);
      border-radius: 8px;
      padding: 12px;
      font-size: 0.7rem;
      overflow: auto;
      max-height: 280px;
    }}
    .foot {{
      margin-top: 28px;
      padding-top: 16px;
      border-top: 1px solid var(--border);
      font-size: 0.8rem;
      color: var(--muted);
    }}
  </style>
</head>
<body>
  <div class="sheet">
    <div class="head">
      <img src="/static/silentverify-logo.png" alt="SilentVerify" />
      <div>
        <h1>SilentVerify Certificate</h1>
        <p>UOV post-quantum state / agent certificate</p>
      </div>
    </div>
    {verify_badge}
    <h2>Identity</h2>
    <dl>
      <dt>Type</dt><dd>{_esc(cert_type)}</dd>
      <dt>Agent DID</dt><dd>{_esc(agent_did)}</dd>
      <dt>Expires</dt><dd>{_esc(expires_s)}</dd>
      <dt>Issued (print)</dt><dd>{_esc(issued_at)}</dd>
    </dl>
    <h2>Cryptography</h2>
    <dl>
      <dt>Schema</dt><dd>{_esc(schema)}</dd>
      <dt>Field (q, o, v)</dt><dd>{_esc(q)}, {_esc(o)}, {_esc(v)}</dd>
      <dt>Digest y</dt><dd>{_esc(_fmt_digest(cert.get("digest_y") or []))}</dd>
      <dt>Public key fp</dt><dd>{_esc(pubkey_fp)}</dd>
    </dl>
    <h2>Wire format (JSON)</h2>
    <pre>{pretty}</pre>
    <p class="foot">
      Verify online at your SilentVerify deployment. This document is a human-readable summary;
      the JSON block is the authoritative certificate for APIs and on-chain tooling.
      <br />A product of COINjecture Network LLC
    </p>
  </div>
  <script>
    if (window.location.search.includes('autoprint=1')) window.onload = () => window.print();
  </script>
</body>
</html>"""
