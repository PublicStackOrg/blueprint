# SPDX-License-Identifier: AGPL-3.0-or-later
# Part of {{ cookiecutter.public_service_name }} (PublicStack).
"""Data-export endpoints — one per entity model.

PublicStack standard: every entity defined in `libraries/core/core/db/models.py`
must expose a working data-export endpoint. The compliance suite enforces
this via the `data_export` check (rule DEX-001).

Returns NDJSON (newline-delimited JSON) so consumers can stream large
datasets without loading the whole result into memory.
"""

from __future__ import annotations

import json
from collections.abc import AsyncIterator

from core.db.models import Item
from fastapi import APIRouter, Depends
from fastapi.responses import StreamingResponse
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from api.dependencies import get_session

router = APIRouter(prefix="/export")


async def _stream_items(session: AsyncSession) -> AsyncIterator[bytes]:
    result = await session.stream(select(Item))
    async for row in result:
        item = row[0]
        yield (
            json.dumps(
                {
                    "id": str(item.id),
                    "name": item.name,
                    "created_at": item.created_at.isoformat(),
                    "updated_at": item.updated_at.isoformat(),
                },
                separators=(",", ":"),
            )
            + "\n"
        ).encode("utf-8")


@router.get("/items")
async def export_items(
    session: AsyncSession = Depends(get_session),
) -> StreamingResponse:
    return StreamingResponse(
        _stream_items(session),
        media_type="application/x-ndjson",
        headers={"X-Content-Type-Options": "nosniff"},
    )
