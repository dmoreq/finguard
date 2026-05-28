#!/usr/bin/env bash
# Prints how to apply archived Supabase migrations (deferred — local dev uses SQLite).
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
MIG_DIR="${ROOT}/docs/archive/supabase/migrations"

echo "Finguard Supabase migrations are archived (not used for local SQLite dev)."
echo "Location: docs/archive/supabase/migrations/"
echo ""
echo "Files (apply in order when you enable Supabase):"
for f in "${MIG_DIR}"/*.sql; do
  echo "  - $(basename "$f")"
done

echo ""
echo "Option A — Supabase CLI (linked project):"
echo "  supabase db push"
echo ""
echo "Option B — SQL Editor: run each file above in filename order."
