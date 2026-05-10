# SPDX-License-Identifier: AGPL-3.0-or-later
"""Local filesystem document_storage adapter."""

from __future__ import annotations

from grid_adapters.document_storage import LocalFilesystemAdapter


def test_local_filesystem_roundtrip(tmp_path):
    adapter = LocalFilesystemAdapter(tmp_path)
    url = adapter.put("hello.txt", b"hi")
    assert url.startswith("file://")
    assert adapter.get("hello.txt") == b"hi"


def test_local_filesystem_nested_keys(tmp_path):
    adapter = LocalFilesystemAdapter(tmp_path)
    adapter.put("a/b/c.txt", b"deep")
    assert adapter.get("a/b/c.txt") == b"deep"
