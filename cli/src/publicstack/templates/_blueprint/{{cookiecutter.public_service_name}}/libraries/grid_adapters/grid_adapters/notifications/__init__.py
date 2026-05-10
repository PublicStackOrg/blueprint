# SPDX-License-Identifier: AGPL-3.0-or-later
"""Notifications adapter — email / SMS / push.

Default impl logs and never sends. Real adapters (SES, Twilio, FCM, etc.)
plug in via NOTIFICATIONS_BACKEND.

The Grid contract is at blueprint/grid/notifications/contract.yaml.
"""

from __future__ import annotations

import logging
import uuid
from dataclasses import dataclass, field
from datetime import UTC, datetime
from typing import Any, Literal, Protocol

Channel = Literal["email", "sms", "push"]
MessageStatus = Literal["queued", "sent", "delivered", "failed", "suppressed"]

logger = logging.getLogger(__name__)


@dataclass(frozen=True)
class Message:
    id: str
    channel: Channel
    status: MessageStatus
    created_at: datetime
    delivered_at: datetime | None = None
    error: str | None = None
    metadata: dict[str, Any] = field(default_factory=dict)


class NotificationsAdapter(Protocol):
    async def send(
        self,
        *,
        channel: Channel,
        to: str,
        template_id: str,
        vars: dict[str, Any] | None = None,
        metadata: dict[str, Any] | None = None,
    ) -> Message: ...

    async def get(self, message_id: str) -> Message | None: ...


class LogOnlyAdapter:
    """Logs notifications and pretends they were delivered."""

    def __init__(self) -> None:
        self._messages: dict[str, Message] = {}

    async def send(
        self,
        *,
        channel: Channel,
        to: str,
        template_id: str,
        vars: dict[str, Any] | None = None,
        metadata: dict[str, Any] | None = None,
    ) -> Message:
        mid = str(uuid.uuid4())
        now = datetime.now(UTC)
        msg = Message(
            id=mid,
            channel=channel,
            status="delivered",  # log-only adapter pretends success
            created_at=now,
            delivered_at=now,
            metadata=metadata or {},
        )
        self._messages[mid] = msg
        logger.info(
            "notification (log-only): id=%s channel=%s to=%s template=%s vars=%s",
            mid, channel, to, template_id, vars or {},
        )
        return msg

    async def get(self, message_id: str) -> Message | None:
        return self._messages.get(message_id)
