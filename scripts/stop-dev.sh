#!/usr/bin/env bash
# Stop local dev processes (backend :5055, Next.js :3000).
set -uo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
FRONTEND="$ROOT/frontend"
RUN_DIR="$ROOT/.dev-lite"

kill_port() {
  local port=$1
  local pids
  pids=$(lsof -ti ":${port}" 2>/dev/null || true)
  if [[ -z "$pids" ]]; then
    return 0
  fi
  echo "Stopping process(es) on :${port} (${pids//$'\n'/ })"
  # shellcheck disable=SC2086
  kill $pids 2>/dev/null || true
  sleep 0.3
  pids=$(lsof -ti ":${port}" 2>/dev/null || true)
  if [[ -n "$pids" ]]; then
    # shellcheck disable=SC2086
    kill -9 $pids 2>/dev/null || true
  fi
}

if [[ -f "$RUN_DIR/backend.pid" ]]; then
  kill "$(cat "$RUN_DIR/backend.pid")" 2>/dev/null || true
fi

kill_port 5055
kill_port 3000

pkill -f "uvicorn actions.server:app" 2>/dev/null || true
pkill -f "${FRONTEND}.*next dev" 2>/dev/null || true
pkill -f "next dev --hostname localhost --port 3000" 2>/dev/null || true

rm -f "$FRONTEND/.next/dev/lock"
rm -rf "$RUN_DIR"

echo "Stopped."
