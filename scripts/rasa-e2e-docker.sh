#!/usr/bin/env bash
# INT-7: Run Rasa e2e tests inside Docker (requires compose stack).
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "${ROOT}/backend"

docker compose run --rm rasa test e2e
