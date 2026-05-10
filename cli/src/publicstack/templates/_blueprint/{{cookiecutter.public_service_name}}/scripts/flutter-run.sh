#!/usr/bin/env bash
# {{ cookiecutter.public_service_name }} — run a Flutter app in Chrome.
#
# Usage: ./scripts/flutter-run.sh <resident|staff|kiosk>
#
# Wires API_BASE_URL via --dart-define so the app talks to the local
# docker-compose api on port 8000.
set -euo pipefail

APP="${1:-resident}"
case "$APP" in
  resident) PORT=3000 ;;
  staff)    PORT=3001 ;;
  kiosk)    PORT=3002 ;;
  *)
    echo "usage: $0 <resident|staff|kiosk>" >&2
    exit 1
    ;;
esac

API_BASE_URL="${API_BASE_URL:-http://localhost:8000}"
ROOT_DIR="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")/.." && pwd)"

cd "$ROOT_DIR/apps/$APP"
flutter run -d chrome --web-port "$PORT" --dart-define="API_BASE_URL=$API_BASE_URL"
