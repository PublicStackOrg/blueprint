# SPDX-License-Identifier: AGPL-3.0-or-later
"""Identity adapter.

Phase 2 ships a no-auth dev stub. The real Grid identity contract and
its default self-hostable implementation land in Phase 4 — see
`blueprint/docs/SPIKES.md` for the open questions on provider choice.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Protocol


@dataclass(frozen=True)
class CurrentUser:
    id: str
    email: str
    is_staff: bool = False


class IdentityAdapter(Protocol):
    async def current_user(self, token: str | None) -> CurrentUser | None: ...


class NoAuthAdapter:
    """Returns a fixed test user regardless of the bearer token.

    Use only when AUTH_MODE=none. Logged so it's obvious the API is
    running without real authentication.
    """

    DEV_USER = CurrentUser(
        id="dev-user",
        email="dev@example.invalid",
        is_staff=True,
    )

    async def current_user(self, token: str | None) -> CurrentUser | None:
        return self.DEV_USER
