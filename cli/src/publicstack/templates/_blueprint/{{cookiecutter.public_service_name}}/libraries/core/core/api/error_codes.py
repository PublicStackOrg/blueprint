# SPDX-License-Identifier: AGPL-3.0-or-later
# Part of {{ cookiecutter.public_service_name }} (PublicStack).
"""Stable error codes returned by the API.

The API serialises every error response as
`{"error_code": str, "error_message": str, "data": dict}`. The
`error_code` value comes from this enum so clients can match against a
known set rather than parsing free-text messages.
"""

from __future__ import annotations

from enum import StrEnum


class ErrorCode(StrEnum):
    NOT_FOUND = "not_found"
    VALIDATION_FAILED = "validation_failed"
    UNAUTHORIZED = "unauthorized"
    FORBIDDEN = "forbidden"
    CONFLICT = "conflict"
    INTERNAL = "internal"
