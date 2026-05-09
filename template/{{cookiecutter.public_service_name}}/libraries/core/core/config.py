# SPDX-License-Identifier: AGPL-3.0-or-later
# Part of {{ cookiecutter.public_service_name }} (PublicStack).
"""Shared settings shape — env-derived, validated by pydantic."""

from __future__ import annotations

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Base settings shared by every internal service in this Public Service.

    Each service can subclass this to add service-specific fields. Loaded
    from environment variables (or a `.env` file in dev).
    """

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )

    environment: str = Field(default="local", description="local | dev | staging | prod")
    log_level: str = Field(default="INFO")

    database_url: str = Field(
        ...,
        description="Async DSN: postgresql+asyncpg://user:pass@host:port/db",
    )
    sync_database_url: str | None = Field(
        default=None,
        description="Sync DSN for Alembic. Derived from database_url if not set.",
    )

    redis_url: str = Field(default="redis://redis:6379/0")

    @property
    def derived_sync_database_url(self) -> str:
        if self.sync_database_url:
            return self.sync_database_url
        return self.database_url.replace("postgresql+asyncpg://", "postgresql://", 1)
