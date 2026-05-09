# SPDX-License-Identifier: AGPL-3.0-or-later
# Part of {{ cookiecutter.public_service_name }} (PublicStack).
"""ORM models for {{ cookiecutter.public_service_name }}.

The blueprint ships a single placeholder `Item` model so the API has a
working CRUD surface end-to-end. Replace it with the real entities for
your Public Service — Parking has Citations, Permits has Applications,
311 has Reports, etc. Whatever you add, the compliance suite (Phase 5)
will require a working data-export endpoint per entity.
"""

from __future__ import annotations

from datetime import UTC, datetime
from uuid import UUID, uuid4

from sqlalchemy import DateTime, String
from sqlalchemy.dialects.postgresql import UUID as PG_UUID
from sqlalchemy.orm import Mapped, mapped_column

from core.db.base import Base


def _now() -> datetime:
    return datetime.now(UTC)


class Item(Base):
    __tablename__ = "items"

    id: Mapped[UUID] = mapped_column(PG_UUID(as_uuid=True), primary_key=True, default=uuid4)
    name: Mapped[str] = mapped_column(String(200), nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=_now, nullable=False)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=_now, onupdate=_now, nullable=False
    )
