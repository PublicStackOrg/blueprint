# Multi-stage build for {{ cookiecutter.service_name }}.
FROM python:3.13-slim AS builder

ENV POETRY_VIRTUALENVS_CREATE=false \
    POETRY_NO_INTERACTION=1 \
    PIP_NO_CACHE_DIR=1

RUN pip install --no-cache-dir "poetry==1.8.3"

WORKDIR /app
COPY services/{{ cookiecutter.service_name }}/pyproject.toml services/{{ cookiecutter.service_name }}/poetry.lock* ./services/{{ cookiecutter.service_name }}/
COPY libraries/ ./libraries/
WORKDIR /app/services/{{ cookiecutter.service_name }}
RUN poetry install --only main --no-root

FROM python:3.13-slim AS runtime
ENV PYTHONUNBUFFERED=1
WORKDIR /app
COPY --from=builder /usr/local/lib/python3.13/site-packages /usr/local/lib/python3.13/site-packages
COPY --from=builder /usr/local/bin /usr/local/bin
COPY libraries/ ./libraries/
COPY services/{{ cookiecutter.service_name }}/ ./services/{{ cookiecutter.service_name }}/
WORKDIR /app/services/{{ cookiecutter.service_name }}
CMD ["uvicorn", "{{ cookiecutter.python_package }}.main:app", "--host", "0.0.0.0", "--port", "8000"]
