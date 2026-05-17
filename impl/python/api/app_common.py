"""Shared app helpers (issuer, responses, chain catalog)."""

from __future__ import annotations

import os
import random
from functools import lru_cache
from typing import Any, Dict, List

from fastapi import HTTPException
from statecert import StateCertificate, StateVerifier
from statecert.issuer import load_verifier, recommended_params
from uov import RandomAdapter

from .models import (
    CertIssueResponse,
    ChainAnchorWire,
    ChainBindingResponse,
    StateCertWire,
)


@lru_cache(maxsize=1)
def load_verifier_instance() -> StateVerifier:
    return load_verifier()


def new_rng() -> RandomAdapter:
    return RandomAdapter(random.Random())


def issue_response(cert: StateCertificate, **extra: Any) -> CertIssueResponse:
    wire = cert.to_wire_dict()
    out = CertIssueResponse(
        status="issued",
        cert=StateCertWire.model_validate(wire),
        pubkey_fp=cert.pubkey_fp,
    )
    if extra:
        return out.model_copy(update=extra)
    return out


def chain_binding_response(
    cert: StateCertificate, binding: Dict[str, Any]
) -> ChainBindingResponse:
    wire = cert.to_wire_dict()
    # binding may be nested under a single key (chain_state, etc.)
    anchor_obj = binding
    if len(binding) == 1:
        anchor_obj = next(iter(binding.values()))
    return ChainBindingResponse(
        status="issued",
        cert=StateCertWire.model_validate(wire),
        pubkey_fp=cert.pubkey_fp,
        anchor=ChainAnchorWire.model_validate(anchor_obj),
    )


def map_chain_error(exc: Exception) -> HTTPException:
    if isinstance(exc, ValueError):
        return HTTPException(status_code=400, detail={"error": "validation_error", "message": str(exc)})
    if isinstance(exc, (OSError, RuntimeError)):
        return HTTPException(status_code=502, detail={"error": "rpc_or_schema", "message": str(exc)})
    return HTTPException(status_code=500, detail={"error": "internal", "message": str(exc)})


_DEV_KEY = os.environ.get("SILENTVERIFY_DEV_API_KEY", "sv_dev_test_key")


def api_description() -> str:
    return f"""SilentVerify — **Agent PKI** + **chain-anchored state certificates** (UOV).

### Quick start (Swagger)
1. Click **Authorize** → paste API key: `{_DEV_KEY}`
2. Try **Agent PKI → Issue agent cert** with the pre-filled example
3. For live chains, use **Chains** routes (fetch RPC anchor + issue, or verify existing cert)

### Route map
| Goal | Endpoint |
|------|----------|
| Agent identity cert | `POST /api/v1/certs/agent/issue` |
| EVM anchor cert (auto-fetch) | `POST /api/v1/chains/evm/issue` |
| Verify cert on live EVM | `POST /api/v1/chains/evm/verify` |
| Solana / Cosmos / XRPL | `/api/v1/chains/{{solana,cosmos,xrp}}/…` |
| Two EVM legs | `/api/v1/chains/evm-cross/…` |
| Heterogeneous L1 pair | `/api/v1/chains/cross-l1/…` |
| List all hooks | `GET /api/v1/chains` |

Legacy paths (`/api/v1/issue/agent-cert`, `/api/v1/evm/verify-state-cert`, …) still work.
"""


def chain_catalog() -> List[Dict[str, Any]]:
    base = "/api/v1/chains"
    return [
        {
            "id": "evm",
            "label": "EVM (Ethereum, L2s, …)",
            "issue": f"{base}/evm/issue",
            "verify": f"{base}/evm/verify",
            "hints": f"{base}/evm/hints",
            "docs": "rpc_url + block + optional caip2_chain_id; rpc_headers for Infura/Alchemy",
        },
        {
            "id": "solana",
            "label": "Solana",
            "issue": f"{base}/solana/issue",
            "verify": f"{base}/solana/verify",
        },
        {
            "id": "cosmos",
            "label": "Cosmos (LCD REST)",
            "issue": f"{base}/cosmos/issue",
            "verify": f"{base}/cosmos/verify",
        },
        {
            "id": "xrp",
            "label": "XRPL",
            "issue": f"{base}/xrp/issue",
            "verify": f"{base}/xrp/verify",
        },
        {
            "id": "evm-cross",
            "label": "Cross-chain (two EVM RPC legs)",
            "issue": f"{base}/evm-cross/issue",
            "verify": f"{base}/evm-cross/verify",
        },
        {
            "id": "cross-l1",
            "label": "Cross-L1 (evm | solana | cosmos | xrp per leg)",
            "issue": f"{base}/cross-l1/issue",
            "verify": f"{base}/cross-l1/verify",
        },
    ]


def params_payload() -> Dict[str, Any]:
    v = load_verifier_instance()
    k = v.key
    return {
        **recommended_params(),
        "issuer": {
            "q": k.q,
            "o": k.o,
            "v": k.v,
            "pubkey_fp": StateVerifier.public_key_fingerprint(k),
        },
        "chains": chain_catalog(),
    }
