"""Minimal models fixture for compliance tests."""

from __future__ import annotations

from sqlalchemy.orm import Mapped, mapped_column

from core.db.base import Base


class Item(Base):
    __tablename__ = "items"
    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str]


class Citation(Base):
    __tablename__ = "citations"
    id: Mapped[int] = mapped_column(primary_key=True)
    amount_cents: Mapped[int]
