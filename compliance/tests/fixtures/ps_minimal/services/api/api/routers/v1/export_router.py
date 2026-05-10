"""Export endpoints (fixture)."""

from fastapi import APIRouter
from fastapi.responses import StreamingResponse

router = APIRouter(prefix="/export")


@router.get("/items")
async def export_items() -> StreamingResponse:
    return StreamingResponse(iter([b"{}"]), media_type="application/x-ndjson")


@router.get("/citations")
async def export_citations() -> StreamingResponse:
    return StreamingResponse(iter([b"{}"]), media_type="application/x-ndjson")
