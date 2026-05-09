# syntax=docker/dockerfile:1.7
# {{ cookiecutter.public_service_name }} — Worker service image.

FROM python:3.13-slim AS builder

ENV POETRY_VERSION=2.2.1 \
    POETRY_VIRTUALENVS_CREATE=false \
    PIP_NO_CACHE_DIR=1 \
    PYTHONDONTWRITEBYTECODE=1

RUN pip install "poetry==${POETRY_VERSION}"

WORKDIR /workspace

COPY libraries/core /workspace/libraries/core
COPY libraries/grid_adapters /workspace/libraries/grid_adapters
COPY services/worker /workspace/services/worker

WORKDIR /workspace/services/worker
RUN poetry install --only main --no-root --no-interaction


FROM python:3.13-slim AS runtime

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

WORKDIR /app

COPY --from=builder /usr/local/lib/python3.13/site-packages /usr/local/lib/python3.13/site-packages
COPY --from=builder /usr/local/bin /usr/local/bin
COPY --from=builder /workspace/libraries /workspace/libraries
COPY --from=builder /workspace/services/worker /app

ENV PYTHONPATH=/app:/workspace/libraries/core:/workspace/libraries/grid_adapters

CMD ["python", "-m", "src.main"]
