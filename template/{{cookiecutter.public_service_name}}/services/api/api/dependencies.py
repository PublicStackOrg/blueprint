# SPDX-License-Identifier: AGPL-3.0-or-later
# Part of {{ cookiecutter.public_service_name }} (PublicStack).
"""FastAPI dependency providers."""

from __future__ import annotations

from collections.abc import AsyncIterator

from fastapi import Depends, Header, Request
from grid_adapters.accessibility import (
    AccessibilityAdapter,
    InMemoryAccessibilityAdapter,
)
from grid_adapters.audit import AuditAdapter, PostgresAuditAdapter
from grid_adapters.document_storage import LocalFilesystemAdapter, StorageAdapter
from grid_adapters.identity import CurrentUser, IdentityAdapter, NoAuthAdapter
from grid_adapters.notifications import LogOnlyAdapter, NotificationsAdapter
from grid_adapters.payments import LogOnlyPaymentsAdapter, PaymentsAdapter
from sqlalchemy.ext.asyncio import AsyncSession

from api.config import APISettings, get_settings


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


# Identity ------------------------------------------------------------------


def get_identity_adapter(
    settings: APISettings = Depends(get_settings),
) -> IdentityAdapter:
    if settings.auth_mode == "none":
        return NoAuthAdapter()
    raise RuntimeError(
        f"AUTH_MODE={settings.auth_mode!r} requires a configured Grid identity "
        "adapter (e.g. Keycloak/ZITADEL/Authentik). See blueprint/grid/identity/."
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


# Audit ---------------------------------------------------------------------


def get_audit_adapter(
    session: AsyncSession = Depends(get_session),
    settings: APISettings = Depends(get_settings),
) -> AuditAdapter:
    backend = getattr(settings, "audit_backend", "postgres")
    if backend == "postgres":
        return PostgresAuditAdapter(session)
    raise RuntimeError(
        f"AUDIT_BACKEND={backend!r} not supported. See blueprint/grid/audit/README.md."
    )


# Document storage ----------------------------------------------------------


def get_storage_adapter(
    settings: APISettings = Depends(get_settings),
) -> StorageAdapter:
    backend = getattr(settings, "document_storage_backend", "local")
    if backend == "local":
        root = getattr(settings, "document_storage_local_root", "/tmp/document_storage")
        return LocalFilesystemAdapter(root)
    raise RuntimeError(
        f"DOCUMENT_STORAGE_BACKEND={backend!r} not supported. "
        "See blueprint/grid/document_storage/README.md."
    )


# Notifications -------------------------------------------------------------


def get_notifications_adapter(
    settings: APISettings = Depends(get_settings),
) -> NotificationsAdapter:
    backend = getattr(settings, "notifications_backend", "log_only")
    if backend == "log_only":
        return LogOnlyAdapter()
    raise RuntimeError(
        f"NOTIFICATIONS_BACKEND={backend!r} not supported. "
        "See blueprint/grid/notifications/README.md."
    )


# Payments ------------------------------------------------------------------


def get_payments_adapter(
    settings: APISettings = Depends(get_settings),
) -> PaymentsAdapter:
    backend = getattr(settings, "payments_backend", "log_only")
    if backend == "log_only":
        return LogOnlyPaymentsAdapter()
    raise RuntimeError(
        f"PAYMENTS_BACKEND={backend!r} not supported. "
        "See blueprint/grid/payments/README.md."
    )


# Accessibility -------------------------------------------------------------


_accessibility_adapter_singleton: AccessibilityAdapter | None = None


def get_accessibility_adapter() -> AccessibilityAdapter:
    """In-memory adapter is single-process; share one instance across requests."""
    global _accessibility_adapter_singleton
    if _accessibility_adapter_singleton is None:
        _accessibility_adapter_singleton = InMemoryAccessibilityAdapter()
    return _accessibility_adapter_singleton
