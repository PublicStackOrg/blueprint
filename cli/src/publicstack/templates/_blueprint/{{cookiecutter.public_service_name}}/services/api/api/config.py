# SPDX-License-Identifier: AGPL-3.0-or-later
# Part of {{ cookiecutter.public_service_name }} (PublicStack).
"""API-specific settings layered on top of `core.config.Settings`."""

from __future__ import annotations

from typing import Literal

from core.config import Settings
from pydantic import Field


class APISettings(Settings):
    api_host: str = Field(default="0.0.0.0")
    api_port: int = Field(default=8000)

    environment: Literal["local", "staging", "prod"] = Field(
        default="local",
        description=(
            "Deployment environment. Gates HTTPS-redirect middleware: "
            "non-local environments enforce HTTPS at the edge."
        ),
    )

    auth_mode: str = Field(
        default="none",
        description=(
            "Identity adapter to use. 'none' = no-auth dev stub. Other "
            "values land when the Grid identity adapter ships in Phase 4."
        ),
    )

    cors_origins: str = Field(
        default="http://localhost:3000,http://localhost:3001,http://localhost:3002",
        description="Comma-separated list of origins allowed to call the API.",
    )

    @property
    def cors_origins_list(self) -> list[str]:
        return [o.strip() for o in self.cors_origins.split(",") if o.strip()]


def get_settings() -> APISettings:
    return APISettings()  # type: ignore[call-arg]
