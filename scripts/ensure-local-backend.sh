#!/usr/bin/env bash
# Start action server + mock Rasa when ports are free (for frontend-only dev).
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

port_up() {
  curl -sf "http://127.0.0.1:$1/health" >/dev/null 2>&1 \
    || curl -sf "http://127.0.0.1:$1/status" >/dev/null 2>&1
}

if ! port_up 5055; then
  echo "==> Starting action server on :5055"
  cd "$BACKEND"
  uv sync --quiet
  uv run uvicorn actions.server:app --host 127.0.0.1 --port 5055 >"$RUN_DIR/actions.log" 2>&1 &
  echo $! >"$RUN_DIR/actions.pid"
  for _ in $(seq 1 15); do
    port_up 5055 && break
    sleep 1
  done
fi

if ! port_up 5005; then
  if [[ -n "${RASA_PRO_LICENSE:-}" ]]; then
    echo "==> Rasa not on :5005 — run: make dev (or: cd backend && docker compose up -d)"
    exit 1
  fi
  echo "==> Starting mock Rasa on :5005"
  cd "$BACKEND"
  uv run python "$ROOT/scripts/mock-rasa.py" >"$RUN_DIR/rasa-mock.log" 2>&1 &
  echo $! >"$RUN_DIR/rasa.pid"
  for _ in $(seq 1 10); do
    port_up 5005 && break
    sleep 1
  done
fi

if ! port_up 5005; then
  echo "Rasa did not start. See $RUN_DIR/rasa-mock.log"
  exit 1
fi
