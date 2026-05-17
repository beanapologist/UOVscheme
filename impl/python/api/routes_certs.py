"""Agent PKI and offline (crypto-only) certificate routes."""

from __future__ import annotations

from typing import Optional

from fastapi import APIRouter, Body, Depends, HTTPException

from statecert import (
    ChainState,
    StateCertificate,
    StateVerifier,
    agent_identity_from_request,
)

from .app_common import issue_response, load_verifier_instance, new_rng
from .deps import enforce_issue_quota, require_api_key
from .models import (
    AGENT_ISSUE_EXAMPLE,
    AGENT_VERIFY_EXAMPLE,
    STATE_ISSUE_EXAMPLE,
    STATE_VERIFY_EXAMPLE,
    AgentCertIssueRequest,
    AgentCertVerifyRequest,
    CertIssueResponse,
    CertVerifyRequest,
    CertVerifyResponse,
    StateCertIssueRequest,
)

router = APIRouter(tags=["Agent PKI"])


def _verify_cert(wire: dict, *, expected_type: Optional[str]) -> CertVerifyResponse:
    try:
        cert = StateCertificate.from_wire_dict(wire)
    except (ValueError, KeyError, TypeError) as e:
        return CertVerifyResponse(valid=False, detail=f"parse_error: {e}")
    cert_type = cert.metadata.get("cert_type")
    if expected_type is not None and cert_type != expected_type:
        return CertVerifyResponse(
            valid=False,
            pubkey_fp=cert.pubkey_fp,
            cert_type=str(cert_type) if cert_type else None,
            detail=f"expected cert_type={expected_type!r}",
        )
    ok = StateVerifier.verify_certificate(cert)
    return CertVerifyResponse(
        valid=ok,
        pubkey_fp=cert.pubkey_fp,
        cert_type=str(cert_type) if cert_type else None,
        detail=None if ok else "signature_or_fingerprint_failed",
    )


@router.post(
    "/api/v1/certs/agent/issue",
    response_model=CertIssueResponse,
    summary="Issue agent certificate",
)
async def issue_agent(
    body: AgentCertIssueRequest = Body(
        ...,
        examples={
            "demo": {
                "summary": "Ready to run — click Execute",
                "value": AGENT_ISSUE_EXAMPLE,
            },
        },
    ),
    ctx: dict = Depends(require_api_key),
) -> CertIssueResponse:
    enforce_issue_quota(ctx)
    try:
        identity = agent_identity_from_request(
            agent_did=body.agent_did,
            capabilities=body.capabilities,
            reputation_hash=body.reputation_hash,
            anchor=body.anchor,
            expires_in_days=body.expires_in_days,
        )
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e)) from e
    cert = load_verifier_instance().issue_for_agent(
        identity, new_rng(), metadata=body.metadata
    )
    return issue_response(cert)


@router.post(
    "/api/v1/certs/agent/verify",
    response_model=CertVerifyResponse,
    summary="Verify agent certificate (crypto only)",
)
async def verify_agent(
    body: AgentCertVerifyRequest = Body(
        examples={
            "demo": {
                "summary": "Ready to run — demo agent cert",
                "value": AGENT_VERIFY_EXAMPLE,
            },
        },
    ),
    _ctx: dict = Depends(require_api_key),
) -> CertVerifyResponse:
    return _verify_cert(body.wire(), expected_type="agent")


@router.post(
    "/api/v1/certs/state/issue",
    response_model=CertIssueResponse,
    summary="Issue state cert from known anchor (no RPC)",
)
async def issue_state_offline(
    body: StateCertIssueRequest = Body(
        ...,
        examples={
            "demo": {
                "summary": "Issue offline state cert (no RPC)",
                "value": STATE_ISSUE_EXAMPLE,
            },
        },
    ),
    ctx: dict = Depends(require_api_key),
) -> CertIssueResponse:
    enforce_issue_quota(ctx)
    state = ChainState(
        chain_id=body.chain_id,
        block_height=body.block_height,
        state_root_hex=body.state_root_hex,
    )
    md = {"flow": "state_anchor", "cert_type": "state", **body.metadata}
    cert = load_verifier_instance().issue_for_chain_state(state, new_rng(), metadata=md)
    return issue_response(cert)


@router.post(
    "/api/v1/certs/verify",
    response_model=CertVerifyResponse,
    summary="Verify any certificate (crypto only, no API key)",
    description="Public endpoint for recipients and auditors. Checks UOV signature only — no chain RPC.",
)
async def verify_cert_public(body: CertVerifyRequest) -> CertVerifyResponse:
    return _verify_cert(body.wire(), expected_type=None)


@router.post(
    "/api/v1/certs/state/verify",
    response_model=CertVerifyResponse,
    summary="Verify state certificate (crypto only)",
    description=(
        "**Workflow:** run **POST /api/v1/certs/state/issue** first, copy the entire "
        "`cert` object from the 200 response, then paste it here. "
        "Checks UOV signature only (no live chain RPC)."
    ),
)
async def verify_state_offline(
    body: CertVerifyRequest = Body(
        examples={
            "demo": {
                "summary": "Ready to run — demo state cert",
                "value": STATE_VERIFY_EXAMPLE,
            },
        },
    ),
    _ctx: dict = Depends(require_api_key),
) -> CertVerifyResponse:
    return _verify_cert(body.wire(), expected_type=None)


# Legacy paths (aliases)
@router.post(
    "/api/v1/issue/agent-cert", response_model=CertIssueResponse, include_in_schema=True
)
async def legacy_issue_agent(
    body: AgentCertIssueRequest, ctx: dict = Depends(require_api_key)
) -> CertIssueResponse:
    return await issue_agent(body, ctx)


@router.post("/api/v1/verify/agent-cert", response_model=CertVerifyResponse)
async def legacy_verify_agent(
    body: CertVerifyRequest, _ctx: dict = Depends(require_api_key)
) -> CertVerifyResponse:
    return await verify_agent(body, _ctx)


@router.post("/api/v1/issue/state-cert", response_model=CertIssueResponse)
async def legacy_issue_state(
    body: StateCertIssueRequest, ctx: dict = Depends(require_api_key)
) -> CertIssueResponse:
    return await issue_state_offline(body, ctx)


@router.post("/api/v1/verify/state-cert", response_model=CertVerifyResponse)
async def legacy_verify_state(
    body: CertVerifyRequest, _ctx: dict = Depends(require_api_key)
) -> CertVerifyResponse:
    return await verify_state_offline(body, _ctx)
