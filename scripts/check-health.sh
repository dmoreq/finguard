#!/usr/bin/env bash
# OPS-5: Quick health checks for local stack.
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
RASA_URL="${RASA_URL:-http://localhost:5005}"
ACTIONS_URL="${ACTIONS_URL:-http://localhost:5055}"

echo "==> Rasa: ${RASA_URL}"
curl -sf "${RASA_URL}/" >/dev/null && echo "  OK" || { echo "  FAIL"; exit 1; }

echo "==> Action server: ${ACTIONS_URL}"
curl -sf "${ACTIONS_URL}/health" >/dev/null && echo "  OK" || { echo "  FAIL"; exit 1; }

echo "==> Next (optional): http://localhost:3000"
if curl -sf -o /dev/null "http://localhost:3000"; then
  echo "  OK"
else
  echo "  SKIP (not running)"
fi

echo "All required checks passed."
