#!/usr/bin/env bash
# INT-1 helper: print migration apply instructions (requires Supabase CLI or dashboard).
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
MIG_DIR="${ROOT}/supabase/migrations"

echo "Finguard migrations (apply in order):"
for f in "${MIG_DIR}"/*.sql; do
  echo "  - $(basename "$f")"
done

echo ""
echo "Option A — Supabase CLI (linked project):"
echo "  supabase db push"
echo ""
echo "Option B — SQL Editor: run each file above in filename order."
echo ""
echo "Option C — psql:"
echo "  for f in ${MIG_DIR}/*.sql; do psql \"\$DATABASE_URL\" -f \"\$f\"; done"
