"""JSON-RPC 2.0 over HTTP POST (stdlib ``urllib``)."""

from __future__ import annotations

import json
from typing import Any, Dict, List, Optional
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen

_DEFAULT_UA = "SilentVerify/1.1 (+https://github.com/beanapologist/UOVscheme)"


def jsonrpc_call(
    rpc_url: str,
    method: str,
    params: List[Any],
    *,
    timeout: float = 30.0,
    headers: Optional[Dict[str, str]] = None,
) -> Any:
    payload = json.dumps(
        {"jsonrpc": "2.0", "id": 1, "method": method, "params": params},
        separators=(",", ":"),
    ).encode()
    hdrs = {
        "Content-Type": "application/json",
        "User-Agent": _DEFAULT_UA,
        "Accept": "application/json",
    }
    if headers:
        hdrs.update(headers)
    req = Request(
        rpc_url,
        data=payload,
        headers=hdrs,
        method="POST",
    )
    try:
        with urlopen(req, timeout=timeout) as resp:  # noqa: S310 — URL supplied by caller
            body = json.loads(resp.read().decode())
    except HTTPError as e:
        hint = ""
        if e.code == 403:
            hint = (
                " — provider may block default clients; set rpc_headers "
                '(e.g. {"Authorization":"Bearer YOUR_KEY"}) or try another rpc_url'
            )
        raise RuntimeError(f"RPC HTTP {e.code}: {e.reason}{hint}") from e
    except URLError as e:
        raise RuntimeError(f"RPC connection failed: {e.reason}") from e
    except json.JSONDecodeError as e:
        raise RuntimeError("RPC response was not valid JSON") from e
    if not isinstance(body, dict):
        raise RuntimeError("RPC response was not a JSON object")
    err = body.get("error")
    if err is not None:
        raise RuntimeError(f"RPC error: {err!r}")
    if "result" not in body:
        raise RuntimeError("RPC response missing result")
    return body["result"]
