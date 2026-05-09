#!/usr/bin/env bash
# {{ cookiecutter.public_service_name }} — wipe local DB and re-run migrations.
#
# Destroys the postgres_data volume. Useful when migrations diverge or
# you want a clean test bed.
set -euo pipefail

ROOT_DIR="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$ROOT_DIR"

docker compose down -v
docker compose up -d --build
