"""Fetch :class:`CosmosCommitment` from a Cosmos REST / LCD base URL (stdlib only)."""

from __future__ import annotations

import base64
import json
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen

from .state_hash import CosmosCommitment


def fetch_cosmos_commitment(
    rest_base: str,
    *,
    chain_id: str,
    height: int | None = None,
    timeout: float = 30.0,
) -> CosmosCommitment:
    """Query ``/cosmos/base/tendermint/v1beta1/blocks/{height|latest}``.

    ``chain_id`` is the Cosmos SDK **chain identifier** (e.g. ``cosmoshub-4``), not the
    REST hostname; it is embedded in the canonical anchor JSON for digest binding.
    """
    base = rest_base.rstrip("/")
    tail = "latest" if height is None else str(int(height))
    url = f"{base}/cosmos/base/tendermint/v1beta1/blocks/{tail}"
    req = Request(url, headers={"Accept": "application/json"}, method="GET")
    try:
        with urlopen(req, timeout=timeout) as resp:  # noqa: S310
            data = json.loads(resp.read().decode())
    except HTTPError as e:
        raise RuntimeError(f"LCD HTTP {e.code}: {e.reason}") from e
    except URLError as e:
        raise RuntimeError(f"LCD connection failed: {e.reason}") from e
    blk = data.get("block")
    if not isinstance(blk, dict):
        raise ValueError("unexpected REST response: missing block object")
    header = blk.get("header")
    if not isinstance(header, dict):
        raise ValueError("missing block.header")
    h_raw = header.get("height")
    app_b64 = header.get("app_hash")
    if not isinstance(h_raw, str) or not isinstance(app_b64, str):
        raise ValueError("missing header.height or header.app_hash")
    hmount = int(h_raw)
    raw = base64.b64decode(app_b64)
    app_hex = "0x" + raw.hex()
    return CosmosCommitment(chain_id=chain_id, height=hmount, app_hash_hex=app_hex)
