#!/usr/bin/env bash
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$ROOT"

echo "==> uv sync + pytest"
uv sync --quiet
uv run pytest tests/ -q

echo "==> action server"
uv run uvicorn actions.server:app --host 127.0.0.1 --port 5055 &
PID=$!
trap 'kill $PID 2>/dev/null || true' EXIT
sleep 2
curl -sf http://127.0.0.1:5055/health | grep -q '"status":"ok"'
echo "    OK"

if command -v docker >/dev/null 2>&1 && docker info >/dev/null 2>&1 && [[ -f .env ]]; then
  echo "==> lite stack smoke (litellm + rasa)"
  set -a
  # shellcheck disable=SC1091
  source .env
  set +a
  uv run litellm --config litellm/config.yaml --port 4000 &
  LPID=$!
  trap 'kill $PID $LPID 2>/dev/null; docker compose down 2>/dev/null || true' EXIT
  sleep 3
  docker compose up -d
  sleep 10
  curl -sf http://127.0.0.1:5005/status >/dev/null && echo "    OK: rasa" || echo "    WARN: rasa"
  docker compose down
else
  echo "    SKIP: docker or .env"
fi

echo "==> done"
