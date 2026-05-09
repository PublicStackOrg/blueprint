#!/usr/bin/env bash
# {{ cookiecutter.public_service_name }} — fail CI if any service-layer
# Dart `catch` block silently swallows an error.
#
# Service code that catches must do at least one of:
#   - rethrow / throw
#   - emit a MutationFailed event onto the AppEventBus
#   - call a logger / ErrorReporter
#
# The `silent-catch` allowlist (one path:lineno per line) lets you opt
# specific cases out — but you owe the next reviewer a comment explaining
# why on the same line.
#
# Pattern lifted from palateful's tools/no-silent-catch-check.sh.

set -euo pipefail

ROOT_DIR="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$ROOT_DIR"

ALLOWLIST="$ROOT_DIR/tools/silent-catch-allowlist.txt"
TARGET_GLOB="apps/*/lib/features/**/services/*.dart"

# Find all `catch` blocks in target files.
mapfile -t MATCHES < <(grep -rn -E '\bcatch\s*\(' apps/*/lib/features 2>/dev/null \
  | grep -E '/services/' || true)

FAIL=0
for line in "${MATCHES[@]}"; do
  file="${line%%:*}"
  rest="${line#*:}"
  lineno="${rest%%:*}"

  # Skip if already in allowlist.
  if [[ -f "$ALLOWLIST" ]] && grep -qE "^${file}:${lineno}(:|$)" "$ALLOWLIST"; then
    continue
  fi

  # Look at the next ~5 lines after the catch for an acceptable handler.
  end_line=$(( lineno + 6 ))
  block=$(sed -n "${lineno},${end_line}p" "$file")

  if echo "$block" | grep -qE '(rethrow\s*;|throw\s+|emit\(|logger\.|log\.|ErrorReporter\.|MutationFailed\()'; then
    continue
  fi

  echo "silent catch at ${file}:${lineno}"
  echo "  → must rethrow, emit MutationFailed, log, or be added to tools/silent-catch-allowlist.txt with a justification."
  FAIL=1
done

if [[ "$FAIL" -ne 0 ]]; then
  exit 1
fi

echo "no-silent-catch-check: ok"
