"""Per-chain issue (fetch + sign) and verify (live anchor binding) hooks."""

from __future__ import annotations

from fastapi import APIRouter, Body, Depends
from fastapi.concurrency import run_in_threadpool

from . import chain_ops
from .app_common import chain_binding_response, map_chain_error
from .deps import enforce_issue_quota, require_api_key
from .models import (
    EVM_ISSUE_EXAMPLE,
    ChainBindingResponse,
    ChainVerifyBinding,
    ChainVerifyResult,
    CosmosChainRequest,
    CosmosVerifyRequest,
    CrossL1IssueRequest,
    CrossL1VerifyRequest,
    EvmChainRequest,
    EvmCrossIssueRequest,
    EvmCrossVerifyRequest,
    EvmVerifyRequest,
    SolanaChainRequest,
    SolanaVerifyRequest,
    XrpChainRequest,
    XrpVerifyRequest,
)

router = APIRouter(prefix="/api/v1/chains", tags=["Chains"])

_EVM_RPC_HINTS = {
    "note": "Many providers return HTTP 403 without a User-Agent or API key. SilentVerify sends a standard User-Agent; use rpc_headers if needed.",
    "mainnet_examples": [
        "https://eth.drpc.org",
        "https://cloudflare-eth.com",
        "https://1rpc.io/eth",
    ],
    "with_api_key": {
        "rpc_url": "https://mainnet.infura.io/v3/YOUR_PROJECT_ID",
        "rpc_headers": {},
    },
    "local_dev": "Set SILENTVERIFY_ALLOW_LOOPBACK_RPC=1 for http://127.0.0.1:8545",
}


@router.get("/evm/hints")
async def evm_rpc_hints() -> dict:
    """Suggested public RPC URLs and auth pattern (no API key required)."""
    return _EVM_RPC_HINTS


async def _issue(fn, ctx: dict, **kwargs) -> ChainBindingResponse:
    enforce_issue_quota(ctx)
    try:
        cert, binding = await run_in_threadpool(fn, **kwargs)
    except Exception as e:
        raise map_chain_error(e) from e
    return chain_binding_response(cert, binding)


async def _verify(fn, **kwargs) -> ChainVerifyResult:
    try:
        result = await run_in_threadpool(fn, **kwargs)
    except Exception as e:
        raise map_chain_error(e) from e
    return ChainVerifyResult(result=ChainVerifyBinding.model_validate(result))


@router.post("/evm/issue", response_model=ChainBindingResponse, summary="Fetch EVM block → issue cert")
async def evm_issue(
    body: EvmChainRequest = Body(
        ...,
        examples={
            "demo": {"summary": "Mainnet via drpc", "value": EVM_ISSUE_EXAMPLE},
        },
    ),
    ctx: dict = Depends(require_api_key),
) -> ChainBindingResponse:
    return await _issue(
        chain_ops.issue_evm,
        ctx,
        rpc_url=body.rpc_url,
        block=body.block,
        caip2_chain_id=body.caip2_chain_id,
        metadata=body.metadata,
        timeout=body.timeout,
        rpc_headers=body.rpc_headers,
    )


@router.post("/evm/verify", response_model=ChainVerifyResult, summary="Verify cert against live EVM RPC")
async def evm_verify(body: EvmVerifyRequest, _ctx: dict = Depends(require_api_key)) -> ChainVerifyResult:
    return await _verify(
        chain_ops.verify_evm,
        rpc_url=body.rpc_url,
        block=body.block,
        certificate_wire=body.wire(),
        caip2_chain_id=body.caip2_chain_id,
        policy=body.policy,
        timeout=body.timeout,
        rpc_headers=body.rpc_headers,
    )


@router.post("/solana/issue", response_model=ChainBindingResponse)
async def solana_issue(
    body: SolanaChainRequest, ctx: dict = Depends(require_api_key)
) -> ChainBindingResponse:
    return await _issue(
        chain_ops.issue_solana,
        ctx,
        rpc_url=body.rpc_url,
        cluster_id=body.cluster_id,
        slot=body.slot,
        commitment=body.commitment,
        metadata=body.metadata,
        timeout=body.timeout,
    )


@router.post("/solana/verify", response_model=ChainVerifyResult)
async def solana_verify(
    body: SolanaVerifyRequest, _ctx: dict = Depends(require_api_key)
) -> ChainVerifyResult:
    return await _verify(
        chain_ops.verify_solana,
        rpc_url=body.rpc_url,
        certificate_wire=body.wire(),
        cluster_id=body.cluster_id,
        slot=body.slot,
        commitment=body.commitment,
        timeout=body.timeout,
    )


@router.post("/cosmos/issue", response_model=ChainBindingResponse)
async def cosmos_issue(
    body: CosmosChainRequest, ctx: dict = Depends(require_api_key)
) -> ChainBindingResponse:
    return await _issue(
        chain_ops.issue_cosmos,
        ctx,
        rest_base=body.rest_base,
        chain_id=body.chain_id,
        height=body.height,
        metadata=body.metadata,
        timeout=body.timeout,
    )


@router.post("/cosmos/verify", response_model=ChainVerifyResult)
async def cosmos_verify(
    body: CosmosVerifyRequest, _ctx: dict = Depends(require_api_key)
) -> ChainVerifyResult:
    return await _verify(
        chain_ops.verify_cosmos,
        rest_base=body.rest_base,
        chain_id=body.chain_id,
        certificate_wire=body.wire(),
        height=body.height,
        timeout=body.timeout,
    )


@router.post("/xrp/issue", response_model=ChainBindingResponse)
async def xrp_issue(body: XrpChainRequest, ctx: dict = Depends(require_api_key)) -> ChainBindingResponse:
    return await _issue(
        chain_ops.issue_xrp,
        ctx,
        rpc_url=body.rpc_url,
        network_id=body.network_id,
        ledger_index=body.ledger_index,
        metadata=body.metadata,
        timeout=body.timeout,
    )


@router.post("/xrp/verify", response_model=ChainVerifyResult)
async def xrp_verify(body: XrpVerifyRequest, _ctx: dict = Depends(require_api_key)) -> ChainVerifyResult:
    return await _verify(
        chain_ops.verify_xrp,
        rpc_url=body.rpc_url,
        certificate_wire=body.wire(),
        network_id=body.network_id,
        ledger_index=body.ledger_index,
        timeout=body.timeout,
    )


@router.post("/evm-cross/issue", response_model=ChainBindingResponse)
async def evm_cross_issue(
    body: EvmCrossIssueRequest, ctx: dict = Depends(require_api_key)
) -> ChainBindingResponse:
    return await _issue(
        chain_ops.issue_evm_cross,
        ctx,
        src=body.src,
        dst=body.dst,
        metadata=body.metadata,
        timeout=body.timeout,
    )


@router.post("/evm-cross/verify", response_model=ChainVerifyResult)
async def evm_cross_verify(
    body: EvmCrossVerifyRequest, _ctx: dict = Depends(require_api_key)
) -> ChainVerifyResult:
    return await _verify(
        chain_ops.verify_evm_cross,
        certificate_wire=body.wire(),
        src=body.src,
        dst=body.dst,
        policy=body.policy,
        timeout=body.timeout,
    )


@router.post("/cross-l1/issue", response_model=ChainBindingResponse)
async def cross_l1_issue(
    body: CrossL1IssueRequest, ctx: dict = Depends(require_api_key)
) -> ChainBindingResponse:
    return await _issue(
        chain_ops.issue_cross_l1,
        ctx,
        src=body.src,
        dst=body.dst,
        metadata=body.metadata,
        timeout=body.timeout,
    )


@router.post("/cross-l1/verify", response_model=ChainVerifyResult)
async def cross_l1_verify(
    body: CrossL1VerifyRequest, _ctx: dict = Depends(require_api_key)
) -> ChainVerifyResult:
    return await _verify(
        chain_ops.verify_cross_l1,
        certificate_wire=body.wire(),
        src=body.src,
        dst=body.dst,
        policy=body.policy,
        timeout=body.timeout,
    )

