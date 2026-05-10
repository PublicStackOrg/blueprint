# SPDX-License-Identifier: AGPL-3.0-or-later
"""Payments adapter.

Default impl logs intents to stdout and never moves money. Real adapters
(Stripe, local-bank, city-merchant) plug in via PAYMENTS_BACKEND. The Grid
contract is at blueprint/grid/payments/contract.yaml.

PublicStack is never merchant of record. The adapter takes amount + currency
+ description and returns a redirect URL the resident is sent to; the
adapter never accepts card data.
"""

from __future__ import annotations

import logging
import uuid
from dataclasses import dataclass, field
from datetime import UTC, datetime
from typing import Any, Protocol


@dataclass(frozen=True)
class Intent:
    id: str
    status: str  # see grid/payments/contract.yaml IntentStatus
    amount_cents: int
    currency: str
    created_at: datetime
    redirect_url: str = ""
    metadata: dict[str, Any] = field(default_factory=dict)


class PaymentsAdapter(Protocol):
    async def create_intent(
        self,
        *,
        amount_cents: int,
        currency: str,
        description: str,
        return_url: str | None = None,
        metadata: dict[str, Any] | None = None,
    ) -> Intent: ...

    async def get_intent(self, intent_id: str) -> Intent | None: ...


class LogOnlyPaymentsAdapter:
    """Records intents in memory and logs to stdout. Never moves money."""

    def __init__(self) -> None:
        self._log = logging.getLogger("grid_adapters.payments")
        self._intents: dict[str, Intent] = {}

    async def create_intent(
        self,
        *,
        amount_cents: int,
        currency: str,
        description: str,
        return_url: str | None = None,
        metadata: dict[str, Any] | None = None,
    ) -> Intent:
        iid = str(uuid.uuid4())
        intent = Intent(
            id=iid,
            status="succeeded",  # log-only adapter: pretend it worked
            amount_cents=amount_cents,
            currency=currency,
            created_at=datetime.now(UTC),
            redirect_url=return_url or "",
            metadata=metadata or {},
        )
        self._intents[iid] = intent
        self._log.info(
            "payments intent (log-only) id=%s amount=%d %s description=%s",
            iid, amount_cents, currency, description,
        )
        return intent

    async def get_intent(self, intent_id: str) -> Intent | None:
        return self._intents.get(intent_id)
