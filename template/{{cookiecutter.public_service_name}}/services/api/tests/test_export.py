# SPDX-License-Identifier: AGPL-3.0-or-later
"""Integration test for the export endpoints.

The compliance suite's data_export check (DEX-002) requires a test
mentioning each entity name in services/api/tests/test_export*.py.
"""

from __future__ import annotations

import pytest


@pytest.mark.asyncio
async def test_export_items_streams_ndjson(client) -> None:
    """POST an item, GET /v1/export/items, assert at least one NDJSON line."""
    create = await client.post("/v1/items", json={"name": "test"})
    assert create.status_code == 201

    response = await client.get("/v1/export/items")
    assert response.status_code == 200
    assert response.headers["content-type"].startswith("application/x-ndjson")
    body = response.text
    lines = [line for line in body.split("\n") if line]
    assert lines
    import json
    payload = json.loads(lines[0])
    assert "id" in payload
    assert "name" in payload
