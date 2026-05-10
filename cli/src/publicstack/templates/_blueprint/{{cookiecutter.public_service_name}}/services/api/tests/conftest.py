# SPDX-License-Identifier: AGPL-3.0-or-later
"""Test fixtures for the API service."""

from __future__ import annotations

import os

# Suppress OpenTelemetry's default exporter noise. Tests don't ship traces.
os.environ.setdefault("OTEL_SDK_DISABLED", "true")
