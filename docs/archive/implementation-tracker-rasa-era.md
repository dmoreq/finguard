# Finguard Rasa CALM Backend — Implementation Tracker

> **Archived:** Superseded May 2026. Current stack: [ARCHITECTURE.md](../ARCHITECTURE.md).

**Project:** Finguard Personal Financial Chat Backend
**Framework:** Rasa CALM 3.9+ with Gemini 2.0 Flash + DeepSeek V3
**Start Date:** 2026-05-27
**Last Updated:** 2026-05-28
**Execution Mode:** Subagent-driven (sequential tasks with spec + quality review)

---

## Overview

**Local-first stack:** **Next.js + Rasa CALM + SQLite**. See [ARCHITECTURE.md](./ARCHITECTURE.md).

**Key docs:**

- [ARCHITECTURE.md](./ARCHITECTURE.md) — Stack overview (start here)
- [runbooks/local-development.md](./runbooks/local-development.md) — `make dev`
- [TEST_STRATEGY.md](./TEST_STRATEGY.md) — QA plan
- Supabase → SQLite cleanup (2026-05-28) — see [low-cost-migration/README.md](./low-cost-migration/README.md)
- [archive/](./archive/) — Superseded Supabase-era plans
- [schemas/chat-payloads.json](../schemas/chat-payloads.json) — Chat webhook payload contract
- This file — Progress and day-to-day status

---

## Phase Status

| Phase | Focus | Status |
|-------|-------|--------|
| **1 — Scaffold** | All backend files, Docker, flows, handlers | ✅ Complete |
| **2 — Stack Verification** | uv.lock, pytest, health, Docker build | 🟡 Partial (Docker train manual) |
| **3 — Database & Gaps** | RPC migration, update handler, profile trigger | 🟡 Migrations in repo; apply to Supabase |
| **4 — Backend Tests** | Handler unit tests with mocked Supabase | ✅ Complete (36 tests) |
| **5 — Frontend Integration** | `/api/chat` bridge, ChatWorkspace | ✅ Complete |
| **5b — Data & Auth consolidation** | Supabase Auth, DB SoT, legacy parse removed | ✅ Complete |
| **5c — Simplify stack** | ARCHITECTURE.md, legacy AI removed | ✅ Complete |
| **0 — Prove it works** | CI, runbook, smoke script, profile migration | 🟡 Code done; Docker/Supabase manual |
| **1 — Clean & align** | DB-driven UI, idempotent confirm, Rasa reports | ✅ Complete |
| **2 — Correct & safe** | Payload validation, rate limit, ADRs | ✅ Hobby tier |
| **3 — Product polish** | Settings, export, forgot password, empty states | ✅ Complete |
| **6 — Hardening & Deploy** | Redis, public Rasa firewall, Playwright | ⭕ Scale tier |

---

## Phase 0 — Prove it works 🟡

| ID | Task | Status |
|----|------|--------|
| INT-1 | Apply migrations to Supabase project | ⭕ Manual (`scripts/apply-migrations.sh`) |
| INT-2 | Profile-on-signup migration in repo | ✅ |
| INT-3 | `docker compose up` + train | ⭕ Manual |
| INT-4 | `rasa train` | ⭕ Manual |
| INT-5 | `scripts/smoke-e2e.sh` | ✅ |
| INT-6 | `docs/runbooks/local-development.md` | ✅ |
| INT-7 | `rasa test e2e` in Docker | ⭕ (`scripts/rasa-e2e-docker.sh`) |
| INT-8 | Verify balance RPC on live Supabase | ⭕ |
| INT-9 | Rasa-down UX + retry | ✅ |
| TST-1/2 | GitHub Actions CI | ✅ |
| OPS-1 | CI workflow | ✅ |
| OPS-5 | `scripts/check-health.sh` | ✅ |
| OPS-7 | Migration lint in CI | ✅ |

---

## Phase 1–3 — Hobby backlog ✅ (code)

| ID | Task | Status |
|----|------|--------|
| CLN-9 | Category slug in DB + display in UI | ✅ |
| FE-1 | Pin next/react versions | ✅ |
| FE-2 | Rasa balance/spending → `ReportData` | ✅ |
| FE-5 | Settings page (currency, timezone) | ✅ |
| FE-6 | Safer markdown (escape HTML) | ✅ |
| FE-7 | Payload validation in map-rasa (type guards) | ✅ |
| FEAT-4–8 | Edit pending, empty state, forgot password, CSV export | ✅ |
| BE-1 | Query audit doc | ✅ |
| BE-3 | session_start sync pending tx | ✅ |
| BE-6 | backend/README.md | ✅ |
| BE-7 | All handler tests | ✅ |
| DOC-2 | production-deploy runbook | ✅ |
| DOC-3/4 | ADRs 001, 002 | ✅ |
| DOC-6 | rasa-custom-payloads.json + golden fixtures | ✅ |
| DOC-7 | README links | ✅ |
| TST-4/5 | Golden fixtures + contract tests | ✅ |
| SEC-5 | balance RPC grants migration | ✅ |
| SEC-6 | In-process `/api/chat` rate limit | ✅ (hobby); Redis at scale |
| OPS-3 | dependabot.yml | ✅ |

---

## Phase 5b — Frontend Supabase consolidation ✅

- [x] `@supabase/ssr` + cookie session middleware
- [x] `/login` + `/auth/callback`
- [x] Chat loads transactions + messages from Supabase (RLS)
- [x] `/api/chat` requires auth; Rasa only
- [x] Removed `localStorage` as source of truth

---

## Environment Checklist

- [x] `uv` installed
- [x] `backend/uv.lock` committed
- [x] `frontend/.env.example` (Supabase + RASA_URL)
- [ ] Docker Desktop running
- [ ] `backend/.env` from `.env.example`
- [ ] Supabase migrations applied (including `20260528100000_balance_rpc_grants.sql`)
- [ ] `frontend/.env.local` configured

---

## Scorecard history

| Date | Vision | Backend | Frontend | Integration | Security | Testing | Ops |
|------|--------|---------|----------|-------------|----------|---------|-----|
| 2026-05-27 (am) | 8 | 7 | 6 | 4 | 5 | 5 | 3 |
| 2026-05-27 (pm) | 8 | 7 | 7 | 5 | 6 | 6 | 5 |
| 2026-05-27 (eve) | **9** | **8** | **8** | **5** | **7** | **7** | **6** |

Integration stays at 5 until Docker happy path is logged; lift to 7+ after INT-3/7/8.

---

## Session Log

### Session 6 (2026-05-27) — Remaining hobby backlog

- Rasa `balance` / `spending_report` → structured `ReportData` in UI
- Category slug/display, session_start pending sync, list/query handler tests
- Settings, CSV export, forgot password, retry on Rasa errors, rate limit
- ADRs, payload schema, golden contract tests, dependabot, health/migration scripts
- 18 vitest, 36 pytest — all passing

### Session 5 (2026-05-27) — Phase 0 + 1 (subagent-driven)

- Profile-on-signup migration, local dev runbook, `smoke-e2e.sh`
- GitHub Actions CI (frontend + backend)
- Removed legacy OpenAI parse; ARCHITECTURE + IMPROVEMENT_PLAN docs
- Frontend: DB-driven pending UI, split reset, chat route tests
- Backend: idempotent confirm, handler tests, drop litellm dep

---

## Next Actions (manual)

1. `./scripts/apply-migrations.sh` then apply to Supabase
2. `cd backend && docker compose up` and `docker compose run --rm rasa train`
3. Happy path from [runbooks/local-development.md](./runbooks/local-development.md)
4. `./scripts/smoke-e2e.sh` and `./scripts/check-health.sh`
5. Scale tier when needed: [production-deploy.md](./runbooks/production-deploy.md), Playwright, Redis tracker
