#!/usr/bin/env bash
# Quick health checks for local stack.
set -euo pipefail

CHAT_BACKEND_URL="${CHAT_BACKEND_URL:-${RASA_URL:-http://localhost:5055}}"

echo "==> Chat backend: ${CHAT_BACKEND_URL}"
curl -sf "${CHAT_BACKEND_URL}/health" >/dev/null && echo "  OK" || { echo "  FAIL"; exit 1; }

echo "==> Next (optional): http://localhost:3000"
if curl -sf -o /dev/null "http://localhost:3000"; then
  echo "  OK"
else
  echo "  SKIP (not running)"
fi

echo "All required checks passed."
