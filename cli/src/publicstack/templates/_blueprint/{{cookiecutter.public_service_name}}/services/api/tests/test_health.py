# SPDX-License-Identifier: AGPL-3.0-or-later
"""Tests for /health and /version.

These intentionally don't touch the database — Phase 5 (the compliance
suite) brings in real CRUD tests against a Postgres service container.
For now, /health and /version are enough to prove the FastAPI app
boots and returns the expected shape.
"""

from __future__ import annotations

from api.main import app
from fastapi.testclient import TestClient

client = TestClient(app)


def test_health():
    response = client.get("/health")
    assert response.status_code == 200
    body = response.json()
    assert body["status"] == "ok"


def test_version():
    response = client.get("/version")
    assert response.status_code == 200
    body = response.json()
    assert "version" in body
    assert "blueprint_version" in body
