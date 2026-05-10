"""{{ cookiecutter.service_name }} — FastAPI entrypoint."""

from __future__ import annotations

from fastapi import FastAPI

app = FastAPI(title="{{ cookiecutter.service_name }}", version="0.0.1")


@app.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok", "service": "{{ cookiecutter.service_name }}"}
