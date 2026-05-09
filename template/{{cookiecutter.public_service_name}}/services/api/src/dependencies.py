# SPDX-License-Identifier: AGPL-3.0-or-later
# Part of {{ cookiecutter.public_service_name }} (PublicStack).
"""FastAPI dependency providers."""

from __future__ import annotations

from collections.abc import AsyncIterator

from fastapi import Depends, Header, Request
from grid_adapters.identity import CurrentUser, IdentityAdapter, NoAuthAdapter
from sqlalchemy.ext.asyncio import AsyncSession

from src.config import APISettings, get_settings


async def get_session(request: Request) -> AsyncIterator[AsyncSession]:
    """Yield a fresh session per request, committing or rolling back at the end."""
    maker = request.app.state.db_session_maker
    async with maker() as session:
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise


def get_identity_adapter(
    settings: APISettings = Depends(get_settings),
) -> IdentityAdapter:
    if settings.auth_mode == "none":
        return NoAuthAdapter()
    raise RuntimeError(
        f"AUTH_MODE={settings.auth_mode!r} requires the Grid identity adapter "
        "(arrives in Phase 4). For now, set AUTH_MODE=none."
    )


async def get_current_user(
    authorization: str | None = Header(default=None),
    adapter: IdentityAdapter = Depends(get_identity_adapter),
) -> CurrentUser:
    token = None
    if authorization and authorization.lower().startswith("bearer "):
        token = authorization.split(" ", 1)[1]
    user = await adapter.current_user(token)
    if user is None:
        from core.api.endpoint import APIException
        from core.api.error_codes import ErrorCode

        raise APIException(
            ErrorCode.UNAUTHORIZED,
            "no current user",
            status_code=401,
        )
    return user
