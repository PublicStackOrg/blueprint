# syntax=docker/dockerfile:1.7
# {{ cookiecutter.public_service_name }} — API service image.
#
# Multi-stage: install with Poetry in a builder, copy site-packages into a
# slim runtime. Workspace path deps are flattened by Poetry's lockfile.

FROM python:3.13-slim AS builder

ENV POETRY_VERSION=2.2.1 \
    POETRY_VIRTUALENVS_CREATE=false \
    PIP_NO_CACHE_DIR=1 \
    PYTHONDONTWRITEBYTECODE=1

RUN pip install "poetry==${POETRY_VERSION}"

WORKDIR /workspace

# Copy every library in one shot — Poetry resolves path-dep paths for
# dev groups too, so test_helper (a dev-only dep of api) needs to exist
# even though `--only main` won't install it.
COPY libraries /workspace/libraries
COPY services/api /workspace/services/api

WORKDIR /workspace/services/api
RUN poetry install --only main --no-root --no-interaction


FROM python:3.13-slim AS runtime

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

WORKDIR /app

COPY --from=builder /usr/local/lib/python3.13/site-packages /usr/local/lib/python3.13/site-packages
COPY --from=builder /usr/local/bin /usr/local/bin
COPY --from=builder /workspace/libraries /workspace/libraries
COPY --from=builder /workspace/services/api /app

ENV PYTHONPATH=/app:/workspace/libraries/core:/workspace/libraries/grid_adapters

EXPOSE 8000

CMD ["uvicorn", "src.main:app", "--host", "0.0.0.0", "--port", "8000"]
