#!/usr/bin/env bash
# Start unified backend on :5055 when port is free (for frontend-only dev).
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
BACKEND="$ROOT/backend"
RUN_DIR="$ROOT/.dev-lite"
mkdir -p "$RUN_DIR"

ROUTER_MODE_PRESET="${ROUTER_MODE:-}"
FINGUARD_DB_PATH_PRESET="${FINGUARD_DB_PATH:-}"

if [[ -f "$BACKEND/.env" ]]; then
  set -a
  # shellcheck disable=SC1091
  source "$BACKEND/.env"
  set +a
fi

if [[ -n "$ROUTER_MODE_PRESET" ]]; then
  export ROUTER_MODE="$ROUTER_MODE_PRESET"
else
  export ROUTER_MODE="${ROUTER_MODE:-keyword}"
fi

if [[ -n "$FINGUARD_DB_PATH_PRESET" ]]; then
  export FINGUARD_DB_PATH="$FINGUARD_DB_PATH_PRESET"
fi

if curl -sf http://127.0.0.1:5055/health >/dev/null 2>&1; then
  exit 0
fi

echo "==> Starting backend on :5055"
cd "$BACKEND"
uv sync --quiet
uv run uvicorn actions.server:app --host 127.0.0.1 --port 5055 >"$RUN_DIR/backend.log" 2>&1 &
echo $! >"$RUN_DIR/backend.pid"

for _ in $(seq 1 15); do
  curl -sf http://127.0.0.1:5055/health >/dev/null 2>&1 && exit 0
  sleep 1
done

echo "Backend did not start. See $RUN_DIR/backend.log"
exit 1
