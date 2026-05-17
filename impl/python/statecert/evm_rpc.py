"""Build :class:`ChainState` from a real EVM chain via JSON-RPC (stdlib only).

Use this on **mainnet**, **Sepolia**, **Holesky**, rollups, or any node that speaks
standard ``eth_chainId`` / ``eth_getBlockByNumber``. The returned
:class:`~statecert.state_hash.ChainState` uses CAIP-2 style ``chain_id`` strings
(``eip155:<decimal chain id>``) so the same canonical JSON feeds the SilentVerify
digest path as any other tool that adopts that convention.

Only **public** RPC URLs (no secrets in query strings you would log) are recommended.
"""

from __future__ import annotations

from typing import Dict, Optional, Union

from .jsonrpc import jsonrpc_call
from .state_hash import ChainState

BlockArg = Union[int, str]


def _block_to_param(block: BlockArg) -> str:
    if isinstance(block, int):
        if block < 0:
            raise ValueError("block height must be non-negative")
        return hex(block)
    if not isinstance(block, str):
        raise TypeError("block must be int or str")
    b = block.strip().lower()
    if b in ("latest", "earliest", "pending"):
        return b
    if b.startswith("0x"):
        return b
    raise ValueError(
        "block string must be 'latest', 'earliest', 'pending', or a 0x-prefixed hex quantity"
    )


def fetch_chain_state_evm(
    rpc_url: str,
    *,
    block: BlockArg = "latest",
    caip2_chain_id: str | None = None,
    timeout: float = 30.0,
    rpc_headers: Optional[Dict[str, str]] = None,
) -> ChainState:
    """Return :class:`ChainState` for ``block`` using ``stateRoot`` from the node.

    If ``caip2_chain_id`` is omitted, ``eth_chainId`` is queried and formatted as
    ``eip155:<id>``. Pass it explicitly to skip that call (must match the RPC network).
    """
    if caip2_chain_id is None:
        raw_id = jsonrpc_call(
            rpc_url, "eth_chainId", [], timeout=timeout, headers=rpc_headers
        )
        if not isinstance(raw_id, str) or not raw_id.startswith("0x"):
            raise ValueError(f"unexpected eth_chainId payload: {raw_id!r}")
        caip2_chain_id = f"eip155:{int(raw_id, 16)}"

    block_param = _block_to_param(block)
    blk = jsonrpc_call(
        rpc_url,
        "eth_getBlockByNumber",
        [block_param, False],
        timeout=timeout,
        headers=rpc_headers,
    )
    if not isinstance(blk, dict):
        raise ValueError(f"unexpected getBlock result type: {type(blk).__name__}")
    num_hex = blk.get("number")
    root_hex = blk.get("stateRoot")
    if not isinstance(num_hex, str) or not isinstance(root_hex, str):
        raise ValueError("block JSON missing number or stateRoot")
    height = int(num_hex, 16)
    return ChainState(
        chain_id=caip2_chain_id,
        block_height=height,
        state_root_hex=root_hex,
    )
