# syntax=docker/dockerfile:1.7
# {{ cookiecutter.public_service_name }} — Migrator service image.
# Single-shot container: runs `alembic upgrade head` and exits.

FROM python:3.13-slim

ENV POETRY_VERSION=2.2.1 \
    POETRY_VIRTUALENVS_CREATE=false \
    PIP_NO_CACHE_DIR=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

RUN pip install "poetry==${POETRY_VERSION}"

WORKDIR /workspace

COPY libraries/core /workspace/libraries/core
COPY services/migrator /workspace/services/migrator

WORKDIR /workspace/services/migrator
RUN poetry install --only main --no-root --no-interaction

ENV PYTHONPATH=/workspace/services/migrator:/workspace/libraries/core

CMD ["alembic", "upgrade", "head"]
