# SPDX-License-Identifier: AGPL-3.0-or-later
"""End-to-end CRUD test for the Item placeholder."""

from __future__ import annotations


async def test_item_crud_roundtrip(async_client):
    # Create
    response = await async_client.post("/v1/items", json={"name": "first"})
    assert response.status_code == 201, response.text
    created = response.json()
    item_id = created["id"]
    assert created["name"] == "first"

    # Read one
    response = await async_client.get(f"/v1/items/{item_id}")
    assert response.status_code == 200
    assert response.json()["id"] == item_id

    # List
    response = await async_client.get("/v1/items")
    assert response.status_code == 200
    assert any(i["id"] == item_id for i in response.json())

    # Delete
    response = await async_client.delete(f"/v1/items/{item_id}")
    assert response.status_code == 204

    # Now 404
    response = await async_client.get(f"/v1/items/{item_id}")
    assert response.status_code == 404


async def test_get_unknown_item_returns_404(async_client):
    response = await async_client.get("/v1/items/00000000-0000-0000-0000-000000000000")
    assert response.status_code == 404
    body = response.json()
    assert body["error_code"] == "not_found"
