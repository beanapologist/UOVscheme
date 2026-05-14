"""Minimal HTTP API for chain-backed certificate checks (stdlib only; no extra pip deps).

Run from ``impl/python``::

    python -m statecert.api_server

Environment:

* ``SILENTVERIFY_API_HOST`` (default ``127.0.0.1``)
* ``SILENTVERIFY_API_PORT`` (default ``8765``)
* ``SILENTVERIFY_CORS_ORIGIN`` (default ``*``) — value for ``Access-Control-Allow-Origin``
* ``SILENTVERIFY_ALLOW_LOOPBACK_RPC`` — set to ``1`` to allow ``localhost`` / private IPs in ``rpc_url`` (dev only)

Routes:

* ``POST /api/v1/evm/verify-state-cert``
* ``POST /api/v1/solana/verify-state-cert``
* ``POST /api/v1/cosmos/verify-state-cert``
* ``POST /api/v1/xrp/verify-state-cert``
"""

from __future__ import annotations

import json
import os
import sys
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from typing import Any, Dict, Optional, Tuple

from .chain_api import (
    verify_cosmos_state_certificate_via_rest,
    verify_evm_state_certificate_via_rpc,
    verify_solana_state_certificate_via_rpc,
    verify_xrp_state_certificate_via_rpc,
)


def _cors_origin() -> str:
    return os.environ.get("SILENTVERIFY_CORS_ORIGIN", "*")


def _send_json(
    handler: BaseHTTPRequestHandler, code: int, body: Dict[str, Any]
) -> None:
    data = json.dumps(body, separators=(",", ":")).encode("utf-8")
    handler.send_response(code)
    handler.send_header("Content-Type", "application/json; charset=utf-8")
    handler.send_header("Content-Length", str(len(data)))
    handler.send_header("Access-Control-Allow-Origin", _cors_origin())
    handler.send_header("Access-Control-Allow-Methods", "GET, POST, OPTIONS")
    handler.send_header(
        "Access-Control-Allow-Headers",
        "Content-Type",
    )
    handler.end_headers()
    handler.wfile.write(data)


def _read_json_object(
    handler: BaseHTTPRequestHandler,
) -> Tuple[Optional[Dict[str, Any]], Optional[Tuple[int, Dict[str, Any]]]]:
    max_body = int(os.environ.get("SILENTVERIFY_MAX_BODY_BYTES", "2097152"))
    try:
        length = int(handler.headers.get("Content-Length", "0"))
    except ValueError:
        return None, (400, {"error": "bad_content_length"})
    if length > max_body:
        return None, (413, {"error": "body_too_large"})
    raw = handler.rfile.read(length)
    try:
        body = json.loads(raw.decode("utf-8"))
    except (UnicodeDecodeError, json.JSONDecodeError) as e:
        return None, (400, {"error": "invalid_json", "detail": str(e)})
    if not isinstance(body, dict):
        return None, (400, {"error": "body_must_be_object"})
    return body, None


def _require_cert(
    body: Dict[str, Any],
) -> Tuple[Optional[Dict[str, Any]], Optional[str]]:
    cert = body.get("certificate")
    if not isinstance(cert, dict):
        return None, "missing_certificate_object"
    return cert, None


class _Handler(BaseHTTPRequestHandler):
    protocol_version = "HTTP/1.1"

    def log_message(self, fmt: str, *args: Any) -> None:
        return

    def do_OPTIONS(self) -> None:  # noqa: N802
        self.send_response(204)
        self.send_header("Access-Control-Allow-Origin", _cors_origin())
        self.send_header("Access-Control-Allow-Methods", "GET, POST, OPTIONS")
        self.send_header(
            "Access-Control-Allow-Headers",
            "Content-Type",
        )
        self.end_headers()

    def do_GET(self) -> None:  # noqa: N802
        if self.path.split("?", 1)[0] in ("/", "/api/v1/health"):
            return _send_json(
                self, 200, {"ok": True, "service": "silentverify-chain-api"}
            )
        return _send_json(self, 404, {"error": "not_found"})

    def do_POST(self) -> None:  # noqa: N802
        path = self.path.split("?", 1)[0]
        body, err = _read_json_object(self)
        if err:
            return _send_json(self, err[0], err[1])
        assert body is not None

        if path == "/api/v1/evm/verify-state-cert":
            return self._post_evm(body)
        if path == "/api/v1/solana/verify-state-cert":
            return self._post_solana(body)
        if path == "/api/v1/cosmos/verify-state-cert":
            return self._post_cosmos(body)
        if path == "/api/v1/xrp/verify-state-cert":
            return self._post_xrp(body)
        return _send_json(self, 404, {"error": "not_found"})

    def _post_evm(self, body: Dict[str, Any]) -> None:
        rpc_url = body.get("rpc_url")
        if not isinstance(rpc_url, str) or not rpc_url.strip():
            return _send_json(self, 400, {"error": "missing_rpc_url"})
        cert, cerr = _require_cert(body)
        if cerr:
            return _send_json(self, 400, {"error": cerr})
        assert cert is not None
        block: Any = body.get("block", "latest")
        if block is not None and not isinstance(block, (int, str)):
            return _send_json(
                self, 400, {"error": "block_must_be_int_or_string_or_omitted"}
            )
        caip2 = body.get("caip2_chain_id")
        if caip2 is not None and not isinstance(caip2, str):
            return _send_json(self, 400, {"error": "caip2_chain_id_must_be_string"})
        try:
            timeout = float(body.get("timeout", 30.0))
        except (TypeError, ValueError):
            return _send_json(self, 400, {"error": "timeout_must_be_number"})
        try:
            result = verify_evm_state_certificate_via_rpc(
                rpc_url,
                block,
                cert,
                caip2_chain_id=caip2,
                timeout=timeout,
            )
        except ValueError as e:
            return _send_json(
                self, 400, {"error": "validation_error", "detail": str(e)}
            )
        except (OSError, RuntimeError) as e:
            return _send_json(self, 502, {"error": "rpc_or_schema", "detail": str(e)})
        return _send_json(self, 200, {"result": result})

    def _post_solana(self, body: Dict[str, Any]) -> None:
        rpc_url = body.get("rpc_url")
        if not isinstance(rpc_url, str) or not rpc_url.strip():
            return _send_json(self, 400, {"error": "missing_rpc_url"})
        cert, cerr = _require_cert(body)
        if cerr:
            return _send_json(self, 400, {"error": cerr})
        assert cert is not None
        cluster_id = body.get("cluster_id", "mainnet-beta")
        if not isinstance(cluster_id, str):
            return _send_json(self, 400, {"error": "cluster_id_must_be_string"})
        slot = body.get("slot")
        if slot is not None and not isinstance(slot, int):
            return _send_json(self, 400, {"error": "slot_must_be_int_or_omitted"})
        commitment = body.get("commitment", "finalized")
        if not isinstance(commitment, str):
            return _send_json(self, 400, {"error": "commitment_must_be_string"})
        try:
            timeout = float(body.get("timeout", 30.0))
        except (TypeError, ValueError):
            return _send_json(self, 400, {"error": "timeout_must_be_number"})
        try:
            result = verify_solana_state_certificate_via_rpc(
                rpc_url,
                cert,
                cluster_id=cluster_id,
                slot=slot,
                commitment=commitment,
                timeout=timeout,
            )
        except ValueError as e:
            return _send_json(
                self, 400, {"error": "validation_error", "detail": str(e)}
            )
        except (OSError, RuntimeError) as e:
            return _send_json(self, 502, {"error": "rpc_or_schema", "detail": str(e)})
        return _send_json(self, 200, {"result": result})

    def _post_cosmos(self, body: Dict[str, Any]) -> None:
        rest_base = body.get("rest_base")
        if not isinstance(rest_base, str) or not rest_base.strip():
            return _send_json(self, 400, {"error": "missing_rest_base"})
        chain_id = body.get("chain_id")
        if not isinstance(chain_id, str) or not chain_id.strip():
            return _send_json(self, 400, {"error": "missing_chain_id"})
        cert, cerr = _require_cert(body)
        if cerr:
            return _send_json(self, 400, {"error": cerr})
        assert cert is not None
        height = body.get("height")
        if height is not None and not isinstance(height, int):
            return _send_json(self, 400, {"error": "height_must_be_int_or_omitted"})
        try:
            timeout = float(body.get("timeout", 30.0))
        except (TypeError, ValueError):
            return _send_json(self, 400, {"error": "timeout_must_be_number"})
        try:
            result = verify_cosmos_state_certificate_via_rest(
                rest_base,
                chain_id.strip(),
                cert,
                height=height,
                timeout=timeout,
            )
        except ValueError as e:
            return _send_json(
                self, 400, {"error": "validation_error", "detail": str(e)}
            )
        except (OSError, RuntimeError) as e:
            return _send_json(self, 502, {"error": "rpc_or_schema", "detail": str(e)})
        return _send_json(self, 200, {"result": result})

    def _post_xrp(self, body: Dict[str, Any]) -> None:
        rpc_url = body.get("rpc_url")
        if not isinstance(rpc_url, str) or not rpc_url.strip():
            return _send_json(self, 400, {"error": "missing_rpc_url"})
        network_id = body.get("network_id")
        if not isinstance(network_id, str) or not network_id.strip():
            return _send_json(self, 400, {"error": "missing_network_id"})
        cert, cerr = _require_cert(body)
        if cerr:
            return _send_json(self, 400, {"error": cerr})
        assert cert is not None
        ledger_index: Any = body.get("ledger_index", "validated")
        if ledger_index is not None and not isinstance(ledger_index, (int, str)):
            return _send_json(
                self, 400, {"error": "ledger_index_must_be_int_or_string_or_omitted"}
            )
        try:
            timeout = float(body.get("timeout", 30.0))
        except (TypeError, ValueError):
            return _send_json(self, 400, {"error": "timeout_must_be_number"})
        try:
            result = verify_xrp_state_certificate_via_rpc(
                rpc_url,
                cert,
                network_id=network_id.strip(),
                ledger_index=ledger_index,
                timeout=timeout,
            )
        except ValueError as e:
            return _send_json(
                self, 400, {"error": "validation_error", "detail": str(e)}
            )
        except (OSError, RuntimeError) as e:
            return _send_json(self, 502, {"error": "rpc_or_schema", "detail": str(e)})
        return _send_json(self, 200, {"result": result})


def main() -> None:
    host = os.environ.get("SILENTVERIFY_API_HOST", "127.0.0.1")
    port = int(os.environ.get("SILENTVERIFY_API_PORT", "8765"))
    httpd = ThreadingHTTPServer((host, port), _Handler)
    print(f"SilentVerify chain API on http://{host}:{port}", file=sys.stderr)
    print(
        "POST /api/v1/evm|solana|cosmos|xrp/verify-state-cert",
        file=sys.stderr,
    )
    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        print("\nShutting down.", file=sys.stderr)


if __name__ == "__main__":
    main()
