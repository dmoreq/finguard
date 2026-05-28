#!/usr/bin/env bash
# Lite local dev: Python backend on :5055 + Next.js in foreground.
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
  [[ -f "$RUN_DIR/backend.pid" ]] && kill "$(cat "$RUN_DIR/backend.pid")" 2>/dev/null || true
  rm -f "$RUN_DIR"/*.pid
}

cleanup_stale_ports() {
  pkill -f "uvicorn actions.server:app" 2>/dev/null || true
}
cleanup_stale_ports
trap stop_all EXIT INT TERM

cd "$BACKEND"
uv sync --quiet

echo "==> Backend http://127.0.0.1:5055 (chat + data API)"
uv run uvicorn actions.server:app --host 127.0.0.1 --port 5055 >"$RUN_DIR/backend.log" 2>&1 &
echo $! >"$RUN_DIR/backend.pid"

sleep 2
curl -sf http://127.0.0.1:5055/health >/dev/null || {
  echo "Backend failed. See $RUN_DIR/backend.log"
  exit 1
}

echo ""
echo "Backend ready. Starting Next.js at http://localhost:3000"
echo "Set CHAT_BACKEND_URL=http://127.0.0.1:5055 in frontend/.env.local"
echo "Logs: $RUN_DIR/backend.log  |  Stop: make down"
echo ""

cd "$ROOT"
unset PORT
exec pnpm frontend:dev
