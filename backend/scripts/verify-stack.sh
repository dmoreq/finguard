#!/usr/bin/env bash
# Smoke-check local backend stack (action server + optional Docker services).
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$ROOT"

echo "==> uv sync + pytest"
uv sync --quiet
uv run pytest tests/ -q

echo "==> action server health (local)"
uv run uvicorn actions.server:app --host 127.0.0.1 --port 5055 &
PID=$!
trap 'kill $PID 2>/dev/null || true' EXIT
sleep 2
curl -sf http://127.0.0.1:5055/health | grep -q '"status":"ok"'
echo "    OK: http://127.0.0.1:5055/health"

if command -v docker >/dev/null 2>&1 && docker info >/dev/null 2>&1; then
  echo "==> docker compose build (action-server)"
  docker compose build action-server

  if [[ -f .env ]]; then
    echo "==> docker compose up (detached, 60s wait)"
    docker compose up -d action-server litellm
    sleep 8
    curl -sf http://127.0.0.1:5055/health >/dev/null && echo "    OK: action-server container"
    curl -sf http://127.0.0.1:4000/health/liveliness >/dev/null 2>&1 \
      || curl -sf http://127.0.0.1:4000/health >/dev/null 2>&1 \
      && echo "    OK: litellm" \
      || echo "    SKIP: litellm health (needs API keys in .env)"
    docker compose down
  else
    echo "    SKIP: copy .env.example to .env to run full compose smoke test"
  fi
else
  echo "    SKIP: Docker not available"
fi

echo "==> done"
