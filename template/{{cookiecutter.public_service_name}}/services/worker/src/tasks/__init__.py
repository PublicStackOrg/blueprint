# SPDX-License-Identifier: AGPL-3.0-or-later
"""Task modules.

Each module here defines plain Python functions that are enqueued by
the API (or other services) via the queue Grid adapter. Importing this
package registers task names so RQ can find them at execution time.
"""

from src.tasks.example_task import echo  # noqa: F401
