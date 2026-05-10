# SPDX-License-Identifier: AGPL-3.0-or-later
"""Notifications adapter — email / SMS / push.

Default impl logs notifications instead of sending them. Real
implementations (SendGrid / Twilio / FCM / etc.) plug in when the Grid
notifications contract ships.
"""

from __future__ import annotations

import logging
from typing import Protocol

logger = logging.getLogger(__name__)


class NotificationsAdapter(Protocol):
    def send(self, *, to: str, subject: str, body: str) -> None: ...


class LogOnlyAdapter:
    def send(self, *, to: str, subject: str, body: str) -> None:
        logger.info(
            "notification (log-only): to=%s subject=%r body=%r",
            to,
            subject,
            body,
        )
