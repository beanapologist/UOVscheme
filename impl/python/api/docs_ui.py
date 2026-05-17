"""Branded Swagger UI and ReDoc (match landing page)."""

from __future__ import annotations

from fastapi.openapi.docs import get_swagger_ui_html


def swagger_html(*, openapi_url: str = "/openapi.json"):
    return get_swagger_ui_html(
        openapi_url=openapi_url,
        title="SilentVerify API",
        swagger_favicon_url="/static/logo.svg",
        swagger_css_url="/static/swagger-theme.css",
        swagger_ui_parameters={
            "persistAuthorization": True,
            "docExpansion": "list",
            "tryItOutEnabled": True,
            "defaultModelsExpandDepth": 0,
            "displayRequestDuration": True,
        },
    )
