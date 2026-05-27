# Finguard Rasa CALM Backend — Implementation Tracker

**Project:** Finguard Personal Financial Chat Backend
**Framework:** Rasa CALM 3.9+ with Gemini 2.0 Flash + DeepSeek V3
**Start Date:** 2026-05-27
**Last Updated:** 2026-05-27
**Execution Mode:** Subagent-driven (sequential tasks with spec + quality review)

---

## Overview

Hobby stack: **Next.js + Rasa CALM + Supabase**. See [ARCHITECTURE.md](./ARCHITECTURE.md) and [IMPROVEMENT_PLAN.md](./IMPROVEMENT_PLAN.md).

**Key Planning Docs:**

- `docs/ARCHITECTURE.md` — Short stack overview (start here)
- `docs/IMPROVEMENT_PLAN.md` — Scorecard actions, cleanup, phases (main backlog)
- `docs/runbooks/local-development.md` — Local setup and happy path
- `docs/SYSTEM_DESIGN_REVIEW.md` — Detailed review when scaling up
- `docs/rasa-calm-backend-plan.md` — Full architecture reference
- `docs/PHASE_1_SUMMARY.md` — What Phase 1 built (35 files)
- This file — Progress and day-to-day status

---

## Phase Status

| Phase | Focus | Status |
|-------|-------|--------|
| **1 — Scaffold** | All backend files, Docker, flows, handlers | ✅ Complete |
| **2 — Stack Verification** | uv.lock, pytest, health, Docker build | 🟡 Partial (Docker train manual) |
| **3 — Database & Gaps** | RPC migration, update handler, profile trigger | 🟡 Migrations in repo; apply to Supabase |
| **4 — Backend Tests** | Handler unit tests with mocked Supabase | ✅ Complete (27 tests) |
| **5 — Frontend Integration** | `/api/chat` bridge, ChatWorkspace | ✅ Complete |
| **5b — Data & Auth consolidation** | Supabase Auth, DB SoT, legacy parse removed | ✅ Complete |
| **5c — Simplify stack** | ARCHITECTURE.md, legacy AI removed | ✅ Complete |
| **0 — Prove it works** | CI, runbook, smoke script, profile migration | 🟡 In progress |
| **1 — Clean & align** | DB-driven UI, idempotent confirm | 🟡 Partial |
| **6 — Hardening & Deploy** | Rate limits, Redis, deploy | ⭕ Pending |

---

## Phase 0 — Prove it works 🟡

| ID | Task | Status |
|----|------|--------|
| INT-1 | Apply migrations to Supabase project | ⭕ Manual |
| INT-2 | Profile-on-signup migration in repo | ✅ |
| INT-3 | `docker compose up` + train | ⭕ Manual |
| INT-4 | `rasa train` | ⭕ Manual |
| INT-5 | `scripts/smoke-e2e.sh` | ✅ |
| INT-6 | `docs/runbooks/local-development.md` | ✅ |
| INT-7 | `rasa test e2e` in Docker | ⭕ |
| INT-8 | Verify balance RPC on live Supabase | ⭕ |
| TST-1/2 | GitHub Actions CI | ✅ |
| OPS-1 | CI workflow | ✅ |

---

## Phase 1 — Clean & align 🟡

| ID | Task | Status |
|----|------|--------|
| CLN-1 | Remove legacy OpenAI parse | ✅ |
| CLN-6 | DB-driven confirm/cancel UI | ✅ |
| CLN-7 | Refetch txs after Rasa (no local merge on confirm) | ✅ |
| CLN-8 | Split clear chat vs clear transactions | ✅ |
| FE-3 | Persist chat message DB ids | ✅ |
| BE-2 | Idempotent confirm | ✅ |
| BE-7 | Handler tests (balance, delete, session_start) | ✅ |
| CLN-4 | Remove unused litellm Python dep | ✅ |
| CLN-9 | Category slug + display label | ⭕ |
| SEC-4 | `/api/chat` auth tests | ✅ |

---

## Phase 5b — Frontend Supabase consolidation ✅

- [x] `@supabase/ssr` + cookie session middleware
- [x] `/login` + `/auth/callback`
- [x] Chat loads transactions + messages from Supabase (RLS)
- [x] `/api/chat` requires auth; Rasa only
- [x] Removed `localStorage` as source of truth

---

## Phase 2 — Stack Verification 🟡

### Done ✅

- [x] `uv sync` → `backend/uv.lock`
- [x] `pytest` — 27 tests
- [x] `scripts/verify-stack.sh`
- [x] `scripts/smoke-e2e.sh`

### Manual ⭕

- [ ] `docker compose build && up`
- [ ] `docker compose run --rm rasa train`
- [ ] Rasa REST smoke with live LLM

---

## Phase 3 — Database & Gaps 🟡

### Done ✅

- [x] `20260527000000_initial_schema.sql`
- [x] `20260527000001_balance_rpc.sql`
- [x] `20260528000000_profile_on_signup.sql`
- [x] `update_transaction` handler + idempotent confirm

### Manual ⭕

- [ ] Apply all migrations to Supabase
- [ ] `rasa test e2e`
- [ ] Live RPC verification

---

## Subagent Task Queue

| # | Task | Status |
|---|------|--------|
| 1 | Reorganize tracker | ✅ Done |
| 2 | Stack verification | 🟡 Partial |
| 3 | Supabase RPC + profile trigger | 🟡 Partial |
| 4 | Backend unit tests (all handlers) | ✅ Done |
| 5 | Frontend Rasa bridge | ✅ Done |
| 6 | Phase 0 CI + runbook + smoke | 🟡 Partial |
| 7 | Phase 1 clean & align | 🟡 Partial |
| 8 | Hardening & deploy | ⭕ Pending |

---

## Environment Checklist

- [x] `uv` installed
- [x] `backend/uv.lock` committed
- [x] `frontend/.env.example` (Supabase + RASA_URL)
- [ ] Docker Desktop running
- [ ] `backend/.env` from `.env.example`
- [ ] Supabase migrations applied
- [ ] `frontend/.env.local` configured

---

## Scorecard history

| Date | Vision | Backend | Frontend | Integration | Security | Testing | Ops |
|------|--------|---------|----------|-------------|----------|---------|-----|
| 2026-05-27 (am) | 8 | 7 | 6 | 4 | 5 | 5 | 3 |
| 2026-05-27 (pm) | 8 | 7 | **7** | **5** | **6** | **6** | **5** |

See [IMPROVEMENT_PLAN.md](./IMPROVEMENT_PLAN.md) §G for next lifts.

---

## Session Log

### Session 5 (2026-05-27) — Phase 0 + 1 (subagent-driven)

- Profile-on-signup migration, local dev runbook, `smoke-e2e.sh`
- GitHub Actions CI (frontend + backend)
- Removed legacy OpenAI parse; ARCHITECTURE + IMPROVEMENT_PLAN docs
- Frontend: DB-driven pending UI, split reset, chat route tests
- Backend: idempotent confirm, handler tests (27 total), drop litellm dep

### Session 4 (2026-05-27) — Phase 5 + handler tests

- `POST /api/chat` Rasa proxy; ChatWorkspace confirm/discard
- Handler unit tests (record, update) + vitest map-rasa

### Session 3 (2026-05-27) — Phase 2 + Phase 3 start

- `uv.lock`, pytest, verify-stack.sh, balance RPC, update handler

### Session 2 (2026-05-27) — Phase 1 Scaffold ✅

Created 35 backend files.

---

## Next Actions

1. Apply `supabase/migrations/*` to your Supabase project
2. `cd backend && docker compose up` and `docker compose run --rm rasa train`
3. Run happy path from [runbooks/local-development.md](./runbooks/local-development.md)
4. `./scripts/smoke-e2e.sh`
5. Phase 2: Rasa payload schemas (DOC-6), category alignment (CLN-9)
