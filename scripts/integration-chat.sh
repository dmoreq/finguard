#!/usr/bin/env bash
# INT-B: Next /api/chat with local backend (requires Next on :3000, backend on :5055).
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
CHAT_URL="${CHAT_BACKEND_URL:-${RASA_URL:-http://127.0.0.1:5055}}"
NEXT_URL="${NEXT_URL:-http://localhost:3000}"

echo "==> Chat backend ${CHAT_URL}"
curl -sf "${CHAT_URL}/health" >/dev/null || {
  echo "Start backend: make dev"
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
