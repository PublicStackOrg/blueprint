"""FastAPI app (fixture)."""

import logging

from fastapi import FastAPI, Request
from fastapi.middleware.httpsredirect import HTTPSRedirectMiddleware
from opentelemetry.instrumentation.fastapi import FastAPIInstrumentor
from prometheus_fastapi_instrumentator import Instrumentator
from pythonjsonlogger import JsonFormatter
from starlette.middleware.base import BaseHTTPMiddleware

logger = logging.getLogger("ps_minimal")
handler = logging.StreamHandler()
handler.setFormatter(JsonFormatter())
logging.getLogger().addHandler(handler)


app = FastAPI(title="ps_minimal")


class CSPMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request, call_next):
        response = await call_next(request)
        response.headers["Content-Security-Policy"] = "default-src 'self'"
        return response


app.add_middleware(HTTPSRedirectMiddleware)
app.add_middleware(CSPMiddleware)

FastAPIInstrumentor().instrument_app(app)
Instrumentator().instrument(app).expose(app, endpoint="/metrics")


@app.exception_handler(Exception)
async def unhandled(request: Request, exc: Exception):
    logger.error(
        "unhandled",
        extra={
            "request_id": request.headers.get("x-request-id", ""),
            "path": str(request.url.path),
            "trace_id": "",
            "service": "ps_minimal",
        },
    )
    raise exc
