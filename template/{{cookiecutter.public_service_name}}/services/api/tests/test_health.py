# SPDX-License-Identifier: AGPL-3.0-or-later
"""Tests for /health and /version."""

from __future__ import annotations


async def test_health(async_client):
    response = await async_client.get("/health")
    assert response.status_code == 200
    body = response.json()
    assert body["status"] == "ok"


async def test_version(async_client):
    response = await async_client.get("/version")
    assert response.status_code == 200
    body = response.json()
    assert "version" in body
    assert "blueprint_version" in body
