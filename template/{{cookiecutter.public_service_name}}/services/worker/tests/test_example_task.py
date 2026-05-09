# SPDX-License-Identifier: AGPL-3.0-or-later
"""Smoke test that the example task runs and returns its input."""

from __future__ import annotations

from worker.tasks.example_task import echo


def test_echo_returns_input():
    assert echo("hello") == "hello"
