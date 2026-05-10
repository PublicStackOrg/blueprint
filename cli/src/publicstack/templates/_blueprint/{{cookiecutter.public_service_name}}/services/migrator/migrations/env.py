# SPDX-License-Identifier: AGPL-3.0-or-later
# Part of {{ cookiecutter.public_service_name }} (PublicStack).
"""Alembic env.py.

Imports every model registered against `core.db.base.Base` so
autogenerate can detect schema drift. New model files added under
`core.db.models` need to be imported here too — keep the imports
explicit so it's obvious what's tracked.
"""

from __future__ import annotations

import os
from logging.config import fileConfig

from alembic import context
from core.db import models  # noqa: F401  -- side-effect: registers Item against Base.metadata
from core.db.base import Base
from sqlalchemy import engine_from_config, pool

config = context.config

if config.config_file_name is not None:
    fileConfig(config.config_file_name)

target_metadata = Base.metadata


def get_database_url() -> str:
    sync = os.environ.get("SYNC_DATABASE_URL")
    if sync:
        return sync
    async_url = os.environ.get("DATABASE_URL")
    if async_url:
        return async_url.replace("postgresql+asyncpg://", "postgresql://", 1)
    raise RuntimeError("Set SYNC_DATABASE_URL or DATABASE_URL before running Alembic.")


def run_migrations_offline() -> None:
    url = get_database_url()
    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
        compare_type=True,
    )
    with context.begin_transaction():
        context.run_migrations()


def run_migrations_online() -> None:
    section = config.get_section(config.config_ini_section) or {}
    section["sqlalchemy.url"] = get_database_url()
    connectable = engine_from_config(
        section,
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,
    )
    with connectable.connect() as connection:
        context.configure(
            connection=connection,
            target_metadata=target_metadata,
            compare_type=True,
        )
        with context.begin_transaction():
            context.run_migrations()


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
