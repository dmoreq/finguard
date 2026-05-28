#!/usr/bin/env bash
# Lite local dev: actions + LiteLLM on host, Rasa in Docker, Next.js in foreground.
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
BACKEND="$ROOT/backend"
RUN_DIR="$ROOT/.dev-lite"
mkdir -p "$RUN_DIR"

if [[ -f "$BACKEND/.env" ]]; then
  set -a
  # shellcheck disable=SC1091
  source "$BACKEND/.env"
  set +a
fi

stop_all() {
  [[ -f "$RUN_DIR/actions.pid" ]] && kill "$(cat "$RUN_DIR/actions.pid")" 2>/dev/null || true
  [[ -f "$RUN_DIR/litellm.pid" ]] && kill "$(cat "$RUN_DIR/litellm.pid")" 2>/dev/null || true
  [[ -f "$RUN_DIR/rasa.pid" ]] && kill "$(cat "$RUN_DIR/rasa.pid")" 2>/dev/null || true
  rm -f "$RUN_DIR"/*.pid
  (cd "$BACKEND" && docker compose down 2>/dev/null) || true
}

# Free ports from a previous dev session
cleanup_stale_ports() {
  pkill -f "uvicorn actions.server:app" 2>/dev/null || true
  pkill -f "litellm --config" 2>/dev/null || true
  pkill -f "mock-rasa.py" 2>/dev/null || true
}
cleanup_stale_ports
trap stop_all EXIT INT TERM

cd "$BACKEND"
uv sync --quiet

echo "==> Action server http://127.0.0.1:5055"
uv run uvicorn actions.server:app --host 127.0.0.1 --port 5055 >"$RUN_DIR/actions.log" 2>&1 &
echo $! >"$RUN_DIR/actions.pid"

sleep 2
curl -sf http://127.0.0.1:5055/health >/dev/null || {
  echo "Action server failed. See $RUN_DIR/actions.log"
  exit 1
}

if [[ -n "${RASA_PRO_LICENSE:-}" ]]; then
  echo "==> LiteLLM http://127.0.0.1:4000"
  uv run litellm --config litellm/config.yaml --port 4000 >"$RUN_DIR/litellm.log" 2>&1 &
  echo $! >"$RUN_DIR/litellm.pid"
  for _ in $(seq 1 30); do
    if curl -sf http://127.0.0.1:4000/health/liveliness >/dev/null 2>&1 \
      || curl -sf http://127.0.0.1:4000/health >/dev/null 2>&1; then
      break
    fi
    sleep 1
  done
  if ! curl -sf http://127.0.0.1:4000/health/liveliness >/dev/null 2>&1 \
    && ! curl -sf http://127.0.0.1:4000/health >/dev/null 2>&1; then
    echo "LiteLLM failed to start. See $RUN_DIR/litellm.log"
    echo "Try: cd backend && uv sync"
    exit 1
  fi
else
  echo "==> LiteLLM skipped (mock Rasa mode)"
fi

if [[ -n "${RASA_PRO_LICENSE:-}" ]]; then
  echo "==> Rasa http://127.0.0.1:5005 (Docker, Rasa Pro)"
  docker compose up -d
  for _ in $(seq 1 45); do
    curl -sf http://127.0.0.1:5005/status >/dev/null 2>&1 && break
    sleep 2
  done
  if ! curl -sf http://127.0.0.1:5005/status >/dev/null 2>&1; then
    echo "Rasa Pro did not start. Check: docker compose -f backend/docker-compose.yml logs rasa"
    exit 1
  fi
else
  echo "==> Rasa http://127.0.0.1:5005 (mock — set RASA_PRO_LICENSE for real CALM)"
  uv run python "$ROOT/scripts/mock-rasa.py" >"$RUN_DIR/rasa-mock.log" 2>&1 &
  echo $! >"$RUN_DIR/rasa.pid"
  sleep 1
  curl -sf http://127.0.0.1:5005/status >/dev/null || {
    echo "Mock Rasa failed. See $RUN_DIR/rasa-mock.log"
    exit 1
  }
fi

echo ""
echo "Backend ready. Starting Next.js at http://localhost:3000"
echo "Logs: $RUN_DIR/*.log  |  Stop everything: make down"
echo ""

cd "$ROOT"
# backend/.env may set PORT=5055 for the action server — do not pass it to Next.js
unset PORT
exec pnpm frontend:dev
