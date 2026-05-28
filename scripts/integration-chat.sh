#!/usr/bin/env bash
# INT-B: Next /api/chat with mock Rasa (requires Next on :3000 and mock on :5005).
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
RASA_URL="${RASA_URL:-http://127.0.0.1:5005}"
NEXT_URL="${NEXT_URL:-http://localhost:3000}"

echo "==> Rasa ${RASA_URL}"
curl -sf "${RASA_URL}/status" >/dev/null || {
  echo "Start mock Rasa: uv run python scripts/mock-rasa.py"
  exit 1
}

echo "==> Next ${NEXT_URL}"
if ! curl -sf -o /dev/null "${NEXT_URL}/chat"; then
  echo "Start Next: make dev or pnpm frontend:dev"
  exit 1
fi

echo "==> POST ${NEXT_URL}/api/chat"
RESP=$(curl -sf -X POST "${NEXT_URL}/api/chat" \
  -H "Content-Type: application/json" \
  -d '{"message":"spent 15 on tea"}')

echo "$RESP" | python3 -c "
import json, sys
body = json.load(sys.stdin)
assert 'messages' in body, body
print('OK', len(body['messages']), 'message(s)')
"

echo "Integration chat check passed."
