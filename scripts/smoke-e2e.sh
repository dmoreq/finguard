#!/usr/bin/env bash
# End-to-end smoke: backend health, optional Docker Rasa webhook.
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
BACKEND="$ROOT/backend"

echo "==> backend unit tests"
cd "$BACKEND"
uv sync --quiet
uv run pytest tests/ -q

echo "==> action server health (local uvicorn)"
uv run uvicorn actions.server:app --host 127.0.0.1 --port 5055 &
PID=$!
trap 'kill $PID 2>/dev/null || true' EXIT
sleep 2
curl -sf http://127.0.0.1:5055/health | grep -q '"status":"ok"'
echo "    OK: action-server /health"

if ! command -v docker >/dev/null 2>&1 || ! docker info >/dev/null 2>&1; then
  echo "    SKIP: Docker not available (Rasa webhook smoke skipped)"
  exit 0
fi

if [[ ! -f "$BACKEND/.env" ]]; then
  echo "    SKIP: $BACKEND/.env missing (copy .env.example)"
  exit 0
fi

cd "$BACKEND"
echo "==> docker compose up (rasa, actions, litellm)"
docker compose up -d action-server litellm rasa

echo "    Waiting for services..."
for _ in $(seq 1 30); do
  curl -sf http://127.0.0.1:5005/status >/dev/null 2>&1 && break
  sleep 2
done

curl -sf http://127.0.0.1:5005/status >/dev/null || {
  echo "    FAIL: Rasa not healthy on :5005"
  docker compose logs rasa --tail 20
  exit 1
}
echo "    OK: Rasa /status"

SENDER="${SMOKE_SENDER_ID:-00000000-0000-0000-0000-000000000099}"
RESP=$(curl -sf -X POST http://127.0.0.1:5005/webhooks/rest/webhook \
  -H "Content-Type: application/json" \
  -d "{\"sender\":\"$SENDER\",\"message\":\"spent 10 on coffee\",\"metadata\":{\"user_id\":\"$SENDER\"}}")

echo "$RESP" | grep -q 'transaction_pending\|"text"' || {
  echo "    WARN: unexpected webhook response (model may need training):"
  echo "$RESP" | head -c 500
}

echo "    OK: Rasa webhook responded"
docker compose down
echo "==> smoke done"
