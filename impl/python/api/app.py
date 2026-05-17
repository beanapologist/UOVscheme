"""
SilentVerify unified API — Agent PKI + all chain hooks (FastAPI).

Run: ``./run_saas.sh`` from ``impl/python`` (see ``api/README.md``).
"""

from __future__ import annotations

import os
import sys
from contextlib import asynccontextmanager

_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if _ROOT not in sys.path:
    sys.path.insert(0, _ROOT)

from pathlib import Path

from fastapi import FastAPI, Request
from fastapi.exceptions import RequestValidationError
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from fastapi.openapi.utils import get_openapi
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.errors import RateLimitExceeded
from slowapi.util import get_remote_address

from . import auth
from .app_common import api_description
from .deps import cors_origins
from .routes_certs import router as certs_router
from .routes_chains import router as chains_router
from .routes_billing import router as billing_router
from .routes_legacy import router as legacy_router
from .routes_meta import router as meta_router
from .routes_print import router as print_router

_STATIC_DIR = Path(__file__).resolve().parent / "static"
_UI_VERSION = "2026-05-16"

limiter = Limiter(key_func=get_remote_address, default_limits=["60/minute"])


def _html_page(name: str) -> FileResponse:
    """Serve static HTML with no-cache so browser reload picks up edits."""
    return FileResponse(
        _STATIC_DIR / name,
        media_type="text/html",
        headers={
            "Cache-Control": "no-store, no-cache, must-revalidate",
            "Pragma": "no-cache",
            "X-SilentVerify-UI": _UI_VERSION,
        },
    )

_DEV_KEY_HINT = os.environ.get("SILENTVERIFY_DEV_API_KEY", "sv_dev_test_key")


@asynccontextmanager
async def lifespan(app: FastAPI):
    auth.init_db()
    yield


app = FastAPI(
    title="SilentVerify API",
    version="1.1.0",
    description=api_description(),
    lifespan=lifespan,
    docs_url=None,
    redoc_url=None,
    openapi_tags=[
        {"name": "Getting started", "description": "Health, params, chain catalog"},
        {"name": "Agent PKI", "description": "Issue & verify agent identity certificates"},
        {"name": "Chains", "description": "Fetch live anchor + issue, or verify cert on-chain"},
        {"name": "Chains (legacy paths)", "description": "Same as Chains; old `/api/v1/evm/...` URLs"},
        {"name": "Billing", "description": "Free keys, Stripe Checkout, usage"},
    ],
)

app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)


@app.exception_handler(RequestValidationError)
async def validation_error_handler(_request: Request, exc: RequestValidationError):
    hints = []
    for err in exc.errors():
        loc = ".".join(str(x) for x in err.get("loc", ()))
        if loc in ("body", ""):
            hints.append(
                "Request body is missing or not JSON. Use the pre-filled Example Value in Swagger, not the generic schema placeholders."
            )
        elif "agent_did" in loc:
            hints.append("Set agent_did (e.g. did:example:acme-agent-7), not the literal word 'string'.")
        elif loc in ("body.cert", "cert", "body.certificate"):
            hints.append(
                "Verify routes need the full cert object from a prior POST …/issue response — run Issue first, then paste the cert field."
            )
        elif "rpc_url" in loc:
            hints.append("Set rpc_url to a public HTTPS endpoint (see GET /api/v1/chains/evm/hints).")
    detail = {"errors": exc.errors()}
    if hints:
        detail["hints"] = list(dict.fromkeys(hints))
    return JSONResponse(status_code=422, content={"detail": detail})


app.add_middleware(
    CORSMiddleware,
    allow_origins=cors_origins(),
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

_PUBLIC = {
    "/",
    "/api/v1/health",
    "/api/v1/params",
    "/api/v1/chains",
    "/api/v1/chains/evm/hints",
    "/api/v1/billing/status",
    "/api/v1/billing/free-key",
    "/api/v1/billing/checkout",
    "/api/v1/billing/webhook",
    "/openapi.json",
    "/docs",
    "/try",
    "/swagger",
    "/redoc",
    "/api/v1/certs/print/demo",
}


def _custom_openapi():
    if app.openapi_schema:
        return app.openapi_schema
    schema = get_openapi(
        title=app.title,
        version=app.version,
        description=app.description,
        routes=app.routes,
    )
    schema.setdefault("components", {}).setdefault("securitySchemes", {})[
        "X-API-Key"
    ] = {
        "type": "apiKey",
        "in": "header",
        "name": "X-API-Key",
        "description": f"Dev key: {_DEV_KEY_HINT}",
    }
    for path, methods in schema.get("paths", {}).items():
        if path in _PUBLIC or path.startswith("/api/v1/billing/session/"):
            continue
        for op in methods.values():
            if isinstance(op, dict):
                op["security"] = [{"X-API-Key": []}]
    app.openapi_schema = schema
    return schema


app.openapi = _custom_openapi  # type: ignore[method-assign]

@app.get("/", include_in_schema=False)
async def landing_page():
    return _html_page("index.html")


@app.get("/docs", include_in_schema=False)
@app.get("/try", include_in_schema=False)
async def try_api_console():
    return _html_page("try.html")


@app.get("/swagger", include_in_schema=False)
async def swagger_ui():
    return _html_page("swagger.html")


@app.get("/redoc", include_in_schema=False)
async def redoc_ui():
    return _html_page("redoc.html")


if _STATIC_DIR.is_dir():
    app.mount("/static", StaticFiles(directory=_STATIC_DIR), name="static")

app.include_router(meta_router)
app.include_router(certs_router)
app.include_router(chains_router)
app.include_router(legacy_router)
app.include_router(billing_router)
app.include_router(print_router)
