# Legacy & Redundancy Cleanup Plan

**Status:** Executed 2026-05-28
**Goal:** Remove dead code from the Supabase/auth era, archive deferred assets, align docs with **local-first (SQLite + localStorage + Rasa)**.

---

## 1. Inventory — what was legacy

| Item | Why redundant | Action |
|------|----------------|--------|
| `frontend/src/lib/supabase/*` | Replaced by SQLite + `/api/data/*` | ✅ Already deleted |
| `frontend/src/middleware.ts`, `auth/callback` | Supabase session | ✅ Already deleted |
| `frontend/src/features/auth/LoginForm.tsx` | No auth | ✅ Already deleted |
| `frontend/src/lib/data/map-db-row.ts` | Supabase row shapes; no callers | **Delete** + tests |
| `frontend/src/lib/env.ts` | `hasRasaConfig()` unused | **Delete** |
| `NEXT_PUBLIC_ACTIONS_URL` | Client no longer calls :5055 directly | **Remove**; server `ACTIONS_URL` only |
| `backend/Caddyfile` | Removed from lite dev | ✅ Already deleted |
| `supabase/migrations/*.sql` | Deferred until auth/cloud | **Archive** under `docs/archive/supabase/` |
| `scripts/apply-migrations.sh` | Supabase-only instructions | **Repurpose** → archive pointer |
| CI `migrations` job | Counts live `supabase/` | **Point** at archive |
| Root `rasa/` directory | Accidental HF cache, not `backend/rasa/` | **Delete** + gitignore `/rasa/` |
| Stale docstrings (“Supabase”) in `actions/` | Misleading | **Fix** |
| Planning docs (pre–local-first) | Contradict current stack | **Archive** to `docs/archive/` |

**Keep (not legacy):**

- `frontend/src/app/login/page.tsx` — redirect stub until auth returns
- `supabase/` → archived SQL for future reuse
- `docs/decisions/001-service-role-in-actions.md` — still valid when Supabase returns
- Mock Rasa + lite dev scripts — current local path

---

## 2. Commit groups (conventional, pre-commit safe)

Execute in order so each commit stays buildable.

| # | Commit type | Scope | Files |
|---|-------------|-------|-------|
| 1 | `feat(backend)` | SQLite persistence, handlers, action REST API | `backend/actions/db/*`, handlers, `server.py`, tests, `pyproject.toml`, `docker-compose.yml`, rasa endpoints |
| 2 | `feat(frontend)` | Local-first UI + API proxies, remove Supabase | `frontend/src/**`, drop supabase/middleware |
| 3 | `chore(dev)` | Lite dev tooling | `Makefile`, `scripts/dev-lite.sh`, `ensure-local-backend.sh`, `mock-rasa.py`, `train-lite.sh`, root `package.json` |
| 4 | `chore` | Remove dead frontend modules | `map-db-row*`, `env.ts`, proxy env simplification |
| 5 | `chore` | Archive Supabase SQL + fix backend comments | `docs/archive/supabase/`, `apply-migrations.sh`, `actions/**` docstrings, CI migrations job |
| 6 | `docs` | Archive superseded plans; refresh tracker | `docs/archive/*.md`, `IMPLEMENTATION_TRACKER.md`, `README.md` |
| 7 | `test` | Test strategy doc + API route tests | `docs/TEST_STRATEGY.md`, `route.test.ts` expansions |

---

## 3. Verification per commit

```bash
cd backend && uv run pytest tests/ -q && uv run ruff check actions tests
cd frontend && pnpm test && pnpm typecheck
```

Pre-commit runs on `git commit` (ruff, biome, commitizen on message).

---

## 4. Out of scope (follow-up)

- Rewriting `docs/rasa-calm-backend-plan.md` in place (archived instead)
- Deleting `docs/decisions/001-service-role-in-actions.md`
- Playwright / expanded unit tests (see `docs/TEST_STRATEGY.md`)
