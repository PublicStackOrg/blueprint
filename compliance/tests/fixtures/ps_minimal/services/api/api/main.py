"""FastAPI app (fixture)."""

from fastapi import FastAPI
from fastapi.middleware.httpsredirect import HTTPSRedirectMiddleware
from starlette.middleware.base import BaseHTTPMiddleware

app = FastAPI(title="ps_minimal")


class CSPMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request, call_next):
        response = await call_next(request)
        response.headers["Content-Security-Policy"] = "default-src 'self'"
        return response


# Only enforce HTTPS outside local dev.
app.add_middleware(HTTPSRedirectMiddleware)
app.add_middleware(CSPMiddleware)
