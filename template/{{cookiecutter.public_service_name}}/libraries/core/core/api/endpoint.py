# SPDX-License-Identifier: AGPL-3.0-or-later
# Part of {{ cookiecutter.public_service_name }} (PublicStack).
"""Framework-agnostic API exception type.

The API service translates `APIException` into FastAPI JSONResponses
in its own middleware. Keeping this class framework-free means
non-API callers (workers, scripts) can raise the same exception type
without pulling FastAPI into their dependency closure.
"""

from __future__ import annotations

from typing import Any

from core.api.error_codes import ErrorCode


class APIException(Exception):
    """Raise from any handler/service layer to signal a structured error.

    The serialised shape (set by the API middleware) is:

        {"error_code": str, "error_message": str, "data": dict}
    """

    def __init__(
        self,
        error_code: ErrorCode,
        message: str,
        *,
        status_code: int = 400,
        data: dict[str, Any] | None = None,
    ) -> None:
        super().__init__(message)
        self.error_code = error_code
        self.message = message
        self.status_code = status_code
        self.data = data or {}
