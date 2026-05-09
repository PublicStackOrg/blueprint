# SPDX-License-Identifier: AGPL-3.0-or-later
"""Queue adapter — async work dispatch.

Default implementation is RQ on Redis. Alternative implementations
(Celery+SQS, Cloud Tasks, RabbitMQ) plug in here when the Grid queue
contract is finalised.
"""

from __future__ import annotations

from typing import Any, Protocol

from redis import Redis
from rq import Queue


class QueueAdapter(Protocol):
    def enqueue(self, func: Any, *args: Any, **kwargs: Any) -> str:
        """Enqueue a task. Returns a job id."""
        ...


class RQQueueAdapter:
    """Default implementation: Redis Queue."""

    def __init__(self, redis_url: str, queue_name: str = "default") -> None:
        self._connection = Redis.from_url(redis_url)
        self._queue = Queue(queue_name, connection=self._connection)

    def enqueue(self, func: Any, *args: Any, **kwargs: Any) -> str:
        job = self._queue.enqueue(func, *args, **kwargs)
        return job.id
