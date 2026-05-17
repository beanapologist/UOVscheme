"""Printable certificate views."""

from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import HTMLResponse

from statecert import StateCertificate, StateVerifier

from .certificate_print import render_certificate_html
from .deps import require_api_key
from .models import CertVerifyRequest

router = APIRouter(prefix="/api/v1/certs", tags=["Certificates"])


@router.post("/print", response_class=HTMLResponse, summary="Printable certificate (HTML)")
async def print_certificate(
    body: CertVerifyRequest,
    autoprint: bool = False,
    _ctx: dict = Depends(require_api_key),
) -> HTMLResponse:
    """Return a print-friendly HTML page. Add ``?autoprint=1`` to open the print dialog."""
    try:
        cert = StateCertificate.from_wire_dict(body.wire())
    except (ValueError, KeyError, TypeError) as e:
        raise HTTPException(status_code=400, detail=f"invalid cert: {e}") from e
    verified = StateVerifier.verify_certificate(cert)
    html = render_certificate_html(cert.to_wire_dict(), verified=verified)
    return HTMLResponse(content=html)


@router.post(
    "/print/public",
    response_class=HTMLResponse,
    summary="Printable certificate (no API key)",
    include_in_schema=True,
)
async def print_certificate_public(
    body: CertVerifyRequest,
    autoprint: bool = False,
) -> HTMLResponse:
    """Anyone with the cert JSON can open a human-readable print view."""
    try:
        cert = StateCertificate.from_wire_dict(body.wire())
    except (ValueError, KeyError, TypeError) as e:
        raise HTTPException(status_code=400, detail=f"invalid cert: {e}") from e
    verified = StateVerifier.verify_certificate(cert)
    html = render_certificate_html(cert.to_wire_dict(), verified=verified)
    return HTMLResponse(content=html)


@router.get("/print/demo", response_class=HTMLResponse, include_in_schema=False)
async def print_demo_certificate() -> HTMLResponse:
    """Demo printable page (no API key). Uses built-in sample cert."""
    from .openapi_examples import sample_agent_cert_wire

    wire = sample_agent_cert_wire()
    try:
        verified = StateVerifier.verify_certificate(StateCertificate.from_wire_dict(wire))
    except Exception:
        verified = None
    return HTMLResponse(content=render_certificate_html(wire, verified=verified))
