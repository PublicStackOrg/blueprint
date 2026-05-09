# SPDX-License-Identifier: AGPL-3.0-or-later
# Part of {{ cookiecutter.public_service_name }} (PublicStack).
"""RQ worker entrypoint.

Run via `python -m worker.main` or `rq worker --url $REDIS_URL default`.
The default queue handles all tasks unless a specific queue name is
passed at startup.
"""

from __future__ import annotations

import logging
import sys

from core.config import Settings
from redis import Redis
from rq import Worker


def main() -> int:
    settings = Settings()  # type: ignore[call-arg]
    logging.basicConfig(level=settings.log_level.upper())
    logger = logging.getLogger(__name__)

    redis_url = settings.redis_url
    queue_names = sys.argv[1:] or ["default"]

    logger.info("worker starting; queues=%s redis_url=%s", queue_names, redis_url)
    connection = Redis.from_url(redis_url)
    worker = Worker(queue_names, connection=connection)
    worker.work(with_scheduler=False)
    return 0


if __name__ == "__main__":
    sys.exit(main())
