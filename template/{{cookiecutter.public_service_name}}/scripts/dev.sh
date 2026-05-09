#!/usr/bin/env bash
# {{ cookiecutter.public_service_name }} — start the local dev stack.
#
# Brings up postgres + redis + migrator + api + worker via Docker
# Compose, then prints the URLs you'll want to point at.
set -euo pipefail

ROOT_DIR="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$ROOT_DIR"

if [[ ! -f .env ]]; then
  echo "no .env found; copying .env.example -> .env"
  cp .env.example .env
fi

docker compose up -d --build

echo
echo "  api:      http://localhost:8000"
echo "  health:   http://localhost:8000/health"
echo "  metrics:  http://localhost:8000/metrics"
echo
echo "  next:"
echo "    npm run flutter:resident   # http://localhost:3000"
echo "    npm run flutter:staff      # http://localhost:3001"
echo "    npm run flutter:kiosk      # http://localhost:3002"
