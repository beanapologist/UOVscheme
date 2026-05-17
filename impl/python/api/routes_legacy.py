"""Legacy URL paths from ``statecert.api_server`` (backward compatible)."""

from __future__ import annotations

from fastapi import APIRouter, Depends

from .deps import require_api_key
from .models import (
    ChainVerifyResult,
    CosmosVerifyRequest,
    CrossL1VerifyRequest,
    EvmCrossVerifyRequest,
    EvmVerifyRequest,
    SolanaVerifyRequest,
    XrpVerifyRequest,
)
from .routes_chains import (
    cross_l1_verify,
    cosmos_verify,
    evm_cross_verify,
    evm_verify,
    solana_verify,
    xrp_verify,
)

router = APIRouter(tags=["Chains (legacy paths)"])


@router.post("/api/v1/evm/verify-state-cert", response_model=ChainVerifyResult)
async def legacy_root_evm(
    body: EvmVerifyRequest, ctx: dict = Depends(require_api_key)
) -> ChainVerifyResult:
    return await evm_verify(body, ctx)


@router.post("/api/v1/evm/cross-verify-state-cert", response_model=ChainVerifyResult)
async def legacy_root_evm_cross(
    body: EvmCrossVerifyRequest, ctx: dict = Depends(require_api_key)
) -> ChainVerifyResult:
    return await evm_cross_verify(body, ctx)


@router.post("/api/v1/cross-l1/verify-state-cert", response_model=ChainVerifyResult)
async def legacy_root_cross_l1(
    body: CrossL1VerifyRequest, ctx: dict = Depends(require_api_key)
) -> ChainVerifyResult:
    return await cross_l1_verify(body, ctx)


@router.post("/api/v1/solana/verify-state-cert", response_model=ChainVerifyResult)
async def legacy_root_solana(
    body: SolanaVerifyRequest, ctx: dict = Depends(require_api_key)
) -> ChainVerifyResult:
    return await solana_verify(body, ctx)


@router.post("/api/v1/cosmos/verify-state-cert", response_model=ChainVerifyResult)
async def legacy_root_cosmos(
    body: CosmosVerifyRequest, ctx: dict = Depends(require_api_key)
) -> ChainVerifyResult:
    return await cosmos_verify(body, ctx)


@router.post("/api/v1/xrp/verify-state-cert", response_model=ChainVerifyResult)
async def legacy_root_xrp(
    body: XrpVerifyRequest, ctx: dict = Depends(require_api_key)
) -> ChainVerifyResult:
    return await xrp_verify(body, ctx)
