# SPDX-License-Identifier: AGPL-3.0-or-later
# Part of {{ cookiecutter.public_service_name }} (PublicStack).
"""v1 router aggregator.

Mount sub-routers from `api/routers/v1/` here.
"""

from __future__ import annotations

from fastapi import APIRouter

from api.routers.v1.export_router import router as export_router
from api.routers.v1.items_router import router as items_router

v1_router = APIRouter()
v1_router.include_router(items_router, prefix="/items", tags=["items"])
v1_router.include_router(export_router, tags=["export"])
