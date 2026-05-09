# SPDX-License-Identifier: AGPL-3.0-or-later
# Part of {{ cookiecutter.public_service_name }} (PublicStack).
"""Error-tracking middleware.

Catches anything that escapes the route layer, logs it with the
request context, and returns a structured 500 to the client. Real
crash-reporting integration (Sentry, etc.) plugs in here later.
"""

from __future__ import annotations

import logging
import uuid

from fastapi import Request
from fastapi.responses import JSONResponse
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.types import ASGIApp

logger = logging.getLogger(__name__)


class ErrorTrackingMiddleware(BaseHTTPMiddleware):
    def __init__(self, app: ASGIApp) -> None:
        super().__init__(app)

    async def dispatch(self, request: Request, call_next):
        request_id = str(uuid.uuid4())
        request.state.request_id = request_id
        try:
            response = await call_next(request)
        except Exception:
            logger.exception(
                "unhandled error",
                extra={"request_id": request_id, "path": request.url.path},
            )
            return JSONResponse(
                status_code=500,
                content={
                    "error_code": "internal",
                    "error_message": "internal server error",
                    "data": {"request_id": request_id},
                },
            )
        response.headers["X-Request-Id"] = request_id
        return response
