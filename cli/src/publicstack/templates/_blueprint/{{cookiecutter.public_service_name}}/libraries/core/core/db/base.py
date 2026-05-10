# SPDX-License-Identifier: AGPL-3.0-or-later
# Part of {{ cookiecutter.public_service_name }} (PublicStack).
"""SQLAlchemy declarative base.

Alembic's `migrations/env.py` imports this `Base` for autogenerate to
discover every model registered against it.
"""

from __future__ import annotations

from sqlalchemy.orm import DeclarativeBase


class Base(DeclarativeBase):
    pass
