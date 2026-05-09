# SPDX-License-Identifier: AGPL-3.0-or-later
# Part of {{ cookiecutter.public_service_name }} (PublicStack).
"""Example CRUD router for the placeholder Item entity.

This exists so the generated Public Service has a working end-to-end
HTTP → DB path out of the box. Replace `Item` with your real entities
(Citation, Permit, Report, …) when you start filling in the domain.
"""

from __future__ import annotations

from uuid import UUID

from fastapi import APIRouter, Depends, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from core.api.endpoint import APIException
from core.api.error_codes import ErrorCode
from core.db.models import Item
from grid_adapters.identity import CurrentUser
from src.dependencies import get_current_user, get_session
from src.schemas import ItemCreate, ItemRead

router = APIRouter()


@router.post("", response_model=ItemRead, status_code=status.HTTP_201_CREATED)
async def create_item(
    payload: ItemCreate,
    session: AsyncSession = Depends(get_session),
    user: CurrentUser = Depends(get_current_user),
) -> ItemRead:
    item = Item(name=payload.name)
    session.add(item)
    await session.flush()
    return ItemRead.model_validate(item)


@router.get("", response_model=list[ItemRead])
async def list_items(
    session: AsyncSession = Depends(get_session),
    user: CurrentUser = Depends(get_current_user),
) -> list[ItemRead]:
    result = await session.execute(select(Item).order_by(Item.created_at.desc()))
    return [ItemRead.model_validate(row) for row in result.scalars().all()]


@router.get("/{item_id}", response_model=ItemRead)
async def get_item(
    item_id: UUID,
    session: AsyncSession = Depends(get_session),
    user: CurrentUser = Depends(get_current_user),
) -> ItemRead:
    item = await session.get(Item, item_id)
    if item is None:
        raise APIException(ErrorCode.NOT_FOUND, "item not found", status_code=404)
    return ItemRead.model_validate(item)


@router.delete("/{item_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_item(
    item_id: UUID,
    session: AsyncSession = Depends(get_session),
    user: CurrentUser = Depends(get_current_user),
) -> None:
    item = await session.get(Item, item_id)
    if item is None:
        raise APIException(ErrorCode.NOT_FOUND, "item not found", status_code=404)
    await session.delete(item)
