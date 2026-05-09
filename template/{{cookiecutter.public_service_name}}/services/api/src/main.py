# SPDX-License-Identifier: AGPL-3.0-or-later
# Part of {{ cookiecutter.public_service_name }} (PublicStack).
"""FastAPI application entrypoint.

Wires lifespan setup, middleware, routers, and observability.
"""

from __future__ import annotations

import logging
from contextlib import asynccontextmanager
from collections.abc import AsyncIterator

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from prometheus_fastapi_instrumentator import Instrumentator

from core.api.endpoint import APIException
from core.db.session import make_engine, make_session_maker
from src.config import get_settings
from src.middleware.error_tracking import ErrorTrackingMiddleware
from src.routers.v1_router import v1_router

logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncIterator[None]:
    settings = get_settings()
    logging.basicConfig(level=settings.log_level.upper())

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

app.add_middleware(ErrorTrackingMiddleware)
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins_list,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


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


@app.get("/health", tags=["meta"])
async def health() -> dict[str, str]:
    return {"status": "ok", "service": "{{ cookiecutter.public_service_slug }}"}


@app.get("/version", tags=["meta"])
async def version() -> dict[str, str]:
    return {"version": app.version, "blueprint_version": "{{ cookiecutter.blueprint_version }}"}


app.include_router(v1_router, prefix="/v1")

Instrumentator().instrument(app).expose(app, endpoint="/metrics")
