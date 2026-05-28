#!/usr/bin/env bash
# Playwright webServer: actions + mock Rasa + Next.js on :3000
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
export FINGUARD_DB_PATH="${FINGUARD_DB_PATH:-$ROOT/backend/data/playwright-e2e.db}"
mkdir -p "$(dirname "$FINGUARD_DB_PATH")"

"$ROOT/scripts/ensure-local-backend.sh"

for _ in $(seq 1 30); do
  curl -sf http://127.0.0.1:5055/health >/dev/null 2>&1 \
    && curl -sf http://127.0.0.1:5005/status >/dev/null 2>&1 && break
  sleep 1
done

cd "$ROOT/frontend"
exec pnpm exec next dev --hostname localhost --port 3000
