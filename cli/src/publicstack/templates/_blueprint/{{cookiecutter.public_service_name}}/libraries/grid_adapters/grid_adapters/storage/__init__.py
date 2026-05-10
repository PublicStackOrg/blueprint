# SPDX-License-Identifier: AGPL-3.0-or-later
"""Object-storage adapter.

Default implementation writes to the local filesystem so the dev loop
runs without any cloud account. S3 / GCS / R2 / MinIO adapters plug in
when the Grid storage contract is finalised.
"""

from __future__ import annotations

from pathlib import Path
from typing import Protocol


class StorageAdapter(Protocol):
    def put(self, key: str, content: bytes) -> str:
        """Store bytes under `key`. Returns a stable retrieval URL."""
        ...

    def get(self, key: str) -> bytes:
        """Retrieve bytes by key."""
        ...


class LocalFilesystemAdapter:
    """Writes objects to a directory on local disk. Dev / single-VPS only."""

    def __init__(self, root: str | Path) -> None:
        self._root = Path(root)
        self._root.mkdir(parents=True, exist_ok=True)

    def put(self, key: str, content: bytes) -> str:
        path = self._root / key
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_bytes(content)
        return f"file://{path.resolve()}"

    def get(self, key: str) -> bytes:
        return (self._root / key).read_bytes()
