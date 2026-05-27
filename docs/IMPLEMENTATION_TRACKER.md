# Finguard Rasa CALM Backend — Implementation Tracker

**Project:** Finguard Personal Financial Chat Backend
**Framework:** Rasa CALM 3.9+ with Gemini 2.0 Flash + DeepSeek V3
**Start Date:** 2026-05-27
**Last Updated:** 2026-05-27
**Execution Mode:** Subagent-driven (sequential tasks with spec + quality review)

---

## Overview

Phase 1 delivered a **full scaffold**. Phase 2 verified **uv lockfile, pytest, and local action server**. Phase 3 started with **balance RPC migration** and **`update_transaction` handler**.

**Key Planning Docs:**
- `docs/SYSTEM_DESIGN_REVIEW.md` — Architecture review, threat model, scorecards, improvement actions
- `docs/rasa-calm-backend-plan.md` — Full architecture and configuration reference
- `docs/PHASE_1_SUMMARY.md` — What Phase 1 built (35 files)
- This file — Progress and day-to-day status

---

## Phase Status

| Phase | Focus | Status |
|-------|-------|--------|
| **1 — Scaffold** | All backend files, Docker, flows, handlers | ✅ Complete |
| **2 — Stack Verification** | uv.lock, pytest, health, Docker build | 🟡 Partial (Docker daemon unavailable locally) |
| **3 — Database & Gaps** | RPC migration, update handler | 🟡 In progress |
| **4 — Backend Tests** | Handler unit tests with mocked Supabase | ✅ Complete |
| **5 — Frontend Integration** | `/api/chat` bridge, ChatWorkspace | ✅ Complete |
| **5b — Data & Auth consolidation** | Supabase Auth, DB SoT, legacy parse gated | ✅ Complete |
| **6 — Hardening & Deploy** | Rate limits, Redis, deploy | ⭕ Pending |

---

## Phase 5b — Frontend Supabase consolidation ✅

- [x] `@supabase/ssr` + cookie session middleware
- [x] `/login` + `/auth/callback`
- [x] Chat loads transactions + messages from Supabase (RLS)
- [x] `/api/chat` requires auth; Rasa only (legacy parse behind `ENABLE_LEGACY_AI_PARSE`)
- [x] Removed `localStorage` as source of truth

---

## Phase 2 — Stack Verification 🟡

### Done ✅

- [x] `uv sync` → `backend/uv.lock` generated
- [x] Fixed `pyproject.toml`: action server uses `rasa-sdk` only (not `rasa[full]` — not on PyPI at 3.9)
- [x] `websockets>=13` override for supabase + rasa-sdk compatibility
- [x] `pytest` — 8 tests (dates + action server health)
- [x] Local action server health: `GET /health` → `{"status":"ok"}`
- [x] `scripts/verify-stack.sh` smoke script
- [x] LiteLLM config uses `os.environ/KEY` syntax
- [x] Rasa container env passes Gemini/DeepSeek keys

### Blocked / manual ⭕

- [ ] `docker compose build` — requires Docker daemon running
- [ ] `docker compose up` — requires `.env` with API keys
- [ ] `docker compose run --rm rasa train`
- [ ] Rasa REST smoke test with live LLM

---

## Phase 3 — Database & Gaps 🟡

### Done ✅

- [x] `supabase/migrations/20260527000001_balance_rpc.sql`
- [x] `actions/handlers/update_transaction.py`
- [x] Registered `action_update_transaction` in `domain.yml`

### Done (Rasa skills) ✅

- [x] **manage_transactions** skill: `confirm_pending_transaction`, `discard_pending_transaction`, `edit_pending_transaction`, `no_pending_transaction`
- [x] `persisted_slots` on record expense/income flows
- [x] `backend/rasa/tests/e2e_test_cases.yml` + fixtures (stubbed actions)

### Remaining ⭕

- [ ] Apply migration to Supabase project
- [ ] Run `rasa test e2e` in Docker after `rasa train`
- [ ] End-to-end test `get_balance_summary` RPC

---

## Subagent Task Queue

| # | Task | Status |
|---|------|--------|
| 1 | Reorganize tracker | ✅ Done |
| 2 | Stack verification | 🟡 Partial |
| 3 | Supabase RPC + update handler | 🟡 Partial |
| 4 | Backend unit tests (handlers) | ✅ Done |
| 5 | Frontend Rasa bridge | ✅ Done |
| 6 | Hardening & deploy | ⭕ Pending |

---

## Environment Checklist

- [x] `uv` installed
- [x] `backend/uv.lock` committed-ready
- [ ] Docker Desktop running
- [ ] `backend/.env` from `.env.example`
- [ ] Supabase migrations applied (initial + balance RPC)
- [ ] `frontend/.env.local` with `RASA_URL` + `FIN_GUARD_DEV_USER_ID`

---

## Session Log

### Session 4 (2026-05-27) — Phase 5 + handler tests

- `POST /api/chat` Rasa proxy with parse fallback
- `ChatWorkspace` uses Rasa; confirm/discard send CALM messages
- Handler unit tests (record, update) + frontend map-rasa vitest tests

### Session 3 (2026-05-27) — Phase 2 + Phase 3 start

- Generated `uv.lock`, fixed dependency conflicts
- Added `tests/` (dates + server health)
- Added `scripts/verify-stack.sh`
- Balance RPC migration + `update_transaction` handler

### Session 2 (2026-05-27) — Phase 1 Scaffold ✅

Created 35 backend files.

---

## Scorecard history

| Date | Vision | Backend | Frontend | Integration | Security | Testing | Ops |
|------|--------|---------|----------|-------------|----------|---------|-----|
| 2026-05-27 | 8 | 7 | 6 | 4 | 5 | 5 | 3 |

See `docs/SYSTEM_DESIGN_REVIEW.md` §9 for actions to raise each score.

---

## Next Actions

1. Start Docker → `cp backend/.env.example backend/.env` → fill keys
2. `cd backend && docker compose build && docker compose up`
3. `docker compose run --rm rasa train`
4. Phase 4: `tests/test_handlers/` with mocked Supabase
5. Phase 5: `frontend/src/app/api/chat/route.ts`
