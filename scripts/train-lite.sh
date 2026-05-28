#!/usr/bin/env bash
# Train Rasa model with LiteLLM on host (same as dev-lite).
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
BACKEND="$ROOT/backend"

if [[ -f "$BACKEND/.env" ]]; then
  set -a
  # shellcheck disable=SC1091
  source "$BACKEND/.env"
  set +a
fi

cd "$BACKEND"
uv sync --quiet

echo "==> LiteLLM (required for CALM training)"
uv run litellm --config litellm/config.yaml --port 4000 &
LITELLM_PID=$!
trap 'kill $LITELLM_PID 2>/dev/null || true' EXIT INT TERM
sleep 3

if [[ -z "${RASA_PRO_LICENSE:-}" ]]; then
  echo "RASA_PRO_LICENSE is required for training. Add it to backend/.env"
  exit 1
fi

echo "==> rasa train"
docker compose run --rm rasa train
kill $LITELLM_PID 2>/dev/null || true
