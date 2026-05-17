"""Health, params, and chain catalog."""

from __future__ import annotations

from typing import Any, Dict

from fastapi import APIRouter

from .app_common import chain_catalog, params_payload
from .models import ChainCatalogResponse

router = APIRouter(tags=["Getting started"])


@router.get("/api/v1/health")
async def health() -> Dict[str, Any]:
    return {
        "ok": True,
        "service": "silentverify",
        "version": "1.1.0",
        "docs": "/docs",
        "chains": "/api/v1/chains",
    }


@router.get("/api/v1/chains", response_model=ChainCatalogResponse)
async def list_chains() -> ChainCatalogResponse:
    return ChainCatalogResponse(chains=chain_catalog())


@router.get("/api/v1/params")
async def params() -> Dict[str, Any]:
    return params_payload()
