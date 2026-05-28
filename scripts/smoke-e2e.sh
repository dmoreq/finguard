#!/usr/bin/env bash
# Smoke: pytest + backend health + chat webhook.
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
BACKEND="$ROOT/backend"
CHAT_URL="${CHAT_BACKEND_URL:-http://127.0.0.1:5055}"

echo "==> backend unit tests"
cd "$BACKEND"
uv sync --quiet
uv run pytest tests/ -q

echo "==> backend health + chat webhook"
uv run uvicorn actions.server:app --host 127.0.0.1 --port 5055 &
PID=$!
trap 'kill $PID 2>/dev/null || true' EXIT
sleep 2
curl -sf http://127.0.0.1:5055/health | grep -q '"status":"ok"'
echo "    OK: /health"

SENDER="${SMOKE_SENDER_ID:-00000000-0000-0000-0000-000000000099}"
RESP=$(curl -sf -X POST "${CHAT_URL}/webhooks/rest/webhook" \
  -H "Content-Type: application/json" \
  -d "{\"sender\":\"$SENDER\",\"message\":\"spent 18 on dining for lunch\",\"metadata\":{\"user_id\":\"$SENDER\"}}")

echo "$RESP" | grep -q 'transaction_pending' || {
  echo "    FAIL: unexpected webhook response:"
  echo "$RESP" | head -c 500
  exit 1
}
echo "    OK: chat webhook"

if curl -sf http://127.0.0.1:3000/chat >/dev/null 2>&1; then
  echo "==> integration chat (Next on :3000)"
  "$ROOT/scripts/integration-chat.sh"
fi

echo "==> smoke done"
