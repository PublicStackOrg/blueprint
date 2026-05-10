# SPDX-License-Identifier: AGPL-3.0-or-later
# Part of {{ cookiecutter.public_service_name }} (PublicStack).
"""FastAPI application entrypoint.

Wires lifespan setup, middleware, routers, and observability.
"""

from __future__ import annotations

import logging
import uuid
from collections.abc import AsyncIterator
from contextlib import asynccontextmanager

from core.api.endpoint import APIException
from core.db.session import make_engine, make_session_maker
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.httpsredirect import HTTPSRedirectMiddleware
from fastapi.responses import JSONResponse
from opentelemetry import trace
from opentelemetry.instrumentation.fastapi import FastAPIInstrumentor
from prometheus_fastapi_instrumentator import Instrumentator
from pythonjsonlogger import jsonlogger
from starlette.middleware.base import BaseHTTPMiddleware

from api.config import get_settings
from api.routers.v1_router import v1_router

logger = logging.getLogger(__name__)


def _configure_logging(level: str) -> None:
    """Replace stdlib basicConfig with a python-json-logger JsonFormatter
    on the root logger so structured fields (request_id, trace_id, ...)
    surface as JSON keys."""
    handler = logging.StreamHandler()
    handler.setFormatter(jsonlogger.JsonFormatter(
        "%(asctime)s %(levelname)s %(name)s %(message)s"
    ))
    root = logging.getLogger()
    root.handlers = [handler]
    root.setLevel(level.upper())


class CSPMiddleware(BaseHTTPMiddleware):
    """Set a basic Content-Security-Policy header on every response.

    `default-src 'self'` is conservative; tighten or relax in your own
    middleware as needed (e.g., to allow a CDN).
    """

    async def dispatch(self, request, call_next):
        response = await call_next(request)
        response.headers.setdefault(
            "Content-Security-Policy", "default-src 'self'"
        )
        return response


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncIterator[None]:
    settings = get_settings()
    _configure_logging(settings.log_level)

    engine = make_engine(settings.database_url)
    app.state.db_engine = engine
    app.state.db_session_maker = make_session_maker(engine)
    app.state.settings = settings

    if settings.auth_mode == "none":
        logger.warning("AUTH_MODE=none — API is running without authentication.")

    try:
        yield
    finally:
        await engine.dispose()


app = FastAPI(
    title="{{ cookiecutter.public_service_name }} API",
    description="{{ cookiecutter.description }}",
    version="0.0.1",
    lifespan=lifespan,
)

settings = get_settings()

# CSP first so it applies to every response, including HTTPS redirects.
app.add_middleware(CSPMiddleware)

# HTTPSRedirectMiddleware only outside local dev (otherwise the dev loop
# can't run on http://localhost).
if settings.environment != "local":
    app.add_middleware(HTTPSRedirectMiddleware)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins_list,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# OpenTelemetry tracing. Configure exporters via OTEL_* env vars; default
# exporter is OTLP gRPC. Tests set OTEL_SDK_DISABLED=true to silence.
FastAPIInstrumentor().instrument_app(app)


@app.exception_handler(APIException)
async def api_exception_handler(request: Request, exc: APIException) -> JSONResponse:
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "error_code": exc.error_code.value,
            "error_message": exc.message,
            "data": exc.data,
        },
    )


@app.exception_handler(Exception)
async def unhandled_exception_handler(request: Request, exc: Exception) -> JSONResponse:
    """Catch-all for anything that escapes route handlers."""
    request_id = str(uuid.uuid4())
    span = trace.get_current_span()
    trace_id = ""
    if span and span.get_span_context().is_valid:
        trace_id = format(span.get_span_context().trace_id, "032x")
    logger.exception(
        "unhandled error",
        extra={
            "request_id": request_id,
            "path": request.url.path,
            "trace_id": trace_id,
            "service": "{{ cookiecutter.public_service_slug }}",
        },
    )
    return JSONResponse(
        status_code=500,
        content={
            "error_code": "internal",
            "error_message": "internal server error",
            "data": {"request_id": request_id},
        },
        headers={"X-Request-Id": request_id},
    )


@app.get("/health", tags=["meta"])
async def health() -> dict[str, str]:
    return {"status": "ok", "service": "{{ cookiecutter.public_service_slug }}"}


@app.get("/version", tags=["meta"])
async def version() -> dict[str, str]:
    return {"version": app.version, "blueprint_version": "{{ cookiecutter.blueprint_version }}"}


app.include_router(v1_router, prefix="/v1")

Instrumentator().instrument(app).expose(app, endpoint="/metrics")
