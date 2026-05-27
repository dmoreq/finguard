# Finguard improvement plan

**Date:** 2026-05-27
**Based on:** [ARCHITECTURE.md](./ARCHITECTURE.md) (hobby stack: **Next.js + Rasa CALM + Supabase**)
**Related:** [SYSTEM_DESIGN_REVIEW.md](./SYSTEM_DESIGN_REVIEW.md) (scorecard rubric), [IMPLEMENTATION_TRACKER.md](./IMPLEMENTATION_TRACKER.md) (day-to-day checkboxes)

This is the **single actionable backlog** to raise every scorecard dimension: cleanup redundant code, finish integrations, add missing features, and defer scale-only work until it hurts.

---

## Principles (do not violate)

From [ARCHITECTURE.md](./ARCHITECTURE.md):

1. All chat goes through **Rasa** — no second NLU path.
2. **Supabase** is the only database for user data.
3. **Money mutations** go through Rasa actions (service role), not ad-hoc browser writes to `transactions`.
4. Add Redis, Caddy hardening, rate limits, and multi-region **only when needed**.

---

## Scorecard snapshot

| Dimension | Was (review) | Now (estimate) | Target | Primary lever |
|-----------|--------------|----------------|--------|----------------|
| Vision / documentation | 8 | **8** | 9 | Runbooks + keep ARCHITECTURE current |
| Backend structure | 7 | **7** | 8 | Query audit, idempotent confirm, slot sync |
| Frontend structure | 6 | **7** | 8 | DB-driven UI, reports from Rasa, pin deps |
| Integration completeness | 4 | **4** | 8 | Docker train + smoke + one happy path |
| Security | 5 | **5** | 8 | Rasa network + payload validation |
| Testing | 5 | **5** | 8 | CI + handler/contract + optional Playwright |
| Ops / CI | 3 | **3** | 7 | GitHub Actions + smoke script |

Update the **Scorecard history** table in `IMPLEMENTATION_TRACKER.md` when a phase completes.

---

## Already done (do not redo)

| Item | Notes |
|------|--------|
| Supabase Auth + SSR cookies | `/login`, middleware, `useSession` |
| DB as source of truth | No `localStorage` for txs/messages |
| `/api/chat` → Rasa only | Legacy `server/ai/*` and `/api/ai/parse` **removed** |
| [ARCHITECTURE.md](./ARCHITECTURE.md) | Short hobby overview |
| Rasa bridge + `map-rasa-responses` | Vitest coverage |
| Handler unit tests (record, update) | Mocked Supabase |
| Balance RPC migration | `get_balance_summary` |
| Pending flows in CALM | confirm / discard / edit |

---

## Workstreams overview

```text
Phase 0 — Prove it works     → Integration 4→6, Ops 3→5
Phase 1 — Clean & align      → Frontend 7→8, Backend 7→8, redundant logic gone
Phase 2 — Correct & safe     → Security 5→7, Testing 5→7
Phase 3 — Product polish     → Features users feel (settings, reports, UX)
Phase 4 — Scale when needed  → Optional tier (deploy, Redis, rate limits)
```

---

## A. Cleanup — legacy & redundant code/logic

**Goal:** One chat path, one pending state story, docs match code.

| ID | Action | Effort | Scorecards | Status |
|----|--------|--------|------------|--------|
| CLN-1 | ~~Remove `server/ai/*`, `/api/ai/parse`, legacy env flags~~ | — | Frontend | ✅ Done |
| CLN-2 | Remove `mapParseResultToChatResponse` references from docs (`SYSTEM_DESIGN_REVIEW`, `nextjs-implementation-plan` stale sections) | S | Vision | ⬜ |
| CLN-3 | Delete empty dirs: `frontend/src/app/api/ai/`, `frontend/src/server/ai/` if still present | S | Frontend | ⬜ |
| CLN-4 | Remove unused `litellm` Python package from `backend/pyproject.toml` if actions never import it | S | Backend | ⬜ |
| CLN-5 | Drop `hasChatConfig` / dev-fallback docs from old README sections in long plans | S | Vision | ⬜ |
| CLN-6 | **Single pending state:** UI confirm/cancel enabled only when `transactions.status === 'pending_confirmation'` | M | Frontend, Integration | ⬜ |
| CLN-7 | Stop duplicating tx in UI on confirm — rely on refetch after Rasa turn (trim `handleConfirm` local merge) | S | Frontend | ⬜ |
| CLN-8 | Split **Reset**: “Clear chat history” vs “Delete all transactions” (no one-click nuke) | S | Frontend | ⬜ |
| CLN-9 | Align category storage: slug in DB + display label in UI (or document lowercase-only) | M | Backend, Frontend | ⬜ |
| CLN-10 | Archive or mark `prototype/` as historical only (README note) | S | Vision | ⬜ |

**Acceptance (cleanup stream):** No references to OpenAI parse in app code or env; confirm button state matches DB; docs list only three runtime pillars (Next, Rasa, Supabase).

---

## B. Integration — make the stack actually run

**Goal:** Documented happy path: sign in → chat → pending card → confirm → Supabase row → dashboard.

| ID | Action | Effort | Scorecards | Depends on |
|----|--------|--------|------------|------------|
| INT-1 | Apply all migrations to dev Supabase (`initial_schema` + `balance_rpc` + profile trigger below) | S | Integration | — |
| INT-2 | Add `supabase/migrations/20260528000000_profile_on_signup.sql` (trigger on `auth.users`) | S | Integration, Backend | INT-1 |
| INT-3 | `docker compose build && docker compose up` — record result in tracker | M | Integration | backend `.env` |
| INT-4 | `docker compose run --rm rasa train` — commit trained model or document volume | M | Integration | INT-3 |
| INT-5 | Add `scripts/smoke-e2e.sh` (health + webhook + optional DB check) — see SYSTEM_DESIGN_REVIEW §11.2 | M | Integration, Ops | INT-3 |
| INT-6 | Manual happy path checklist in `docs/runbooks/local-development.md` | S | Vision, Integration | INT-3 |
| INT-7 | Run `rasa test e2e` in Docker (stubbed actions) | M | Integration, Testing | INT-4 |
| INT-8 | Verify `get_balance_summary` RPC against real Supabase | S | Integration, Backend | INT-1 |
| INT-9 | Frontend: surface clear error when Rasa down (already 503 — verify copy + retry) | S | Frontend | — |

**Exit criteria (Phase 0):** One session log in tracker: email signup → “spent $10 on coffee” → confirm → `transactions` row `confirmed` → dashboard shows expense.

### Profile-on-signup migration (INT-2)

```sql
-- supabase/migrations/20260528000000_profile_on_signup.sql
create or replace function public.handle_new_user()
returns trigger language plpgsql security definer set search_path = public as $$
begin
  insert into public.profiles (id, display_name)
  values (
    new.id,
    coalesce(new.raw_user_meta_data->>'display_name', split_part(new.email, '@', 1))
  )
  on conflict (id) do nothing;
  return new;
end;
$$;

create trigger on_auth_user_created
  after insert on auth.users
  for each row execute function public.handle_new_user();
```

---

## C. Scorecard actions (detailed)

### C.1 Vision / documentation (8 → 9)

| ID | Action | Effort | Tier |
|----|--------|--------|------|
| DOC-1 | `docs/runbooks/local-development.md` — Supabase, Docker, env, happy path | S | Hobby |
| DOC-2 | `docs/runbooks/production-deploy.md` — Vercel + VPS + firewall (defer until deploy) | M | Scale |
| DOC-3 | `docs/decisions/001-service-role-in-actions.md` — why service role + `user_id` in every query | S | Hobby |
| DOC-4 | `docs/decisions/002-rasa-network-trust.md` — Rasa not public without secret | S | Scale |
| DOC-5 | Keep `IMPLEMENTATION_TRACKER.md` + this plan in sync each session | S | Hobby |
| DOC-6 | `docs/schemas/rasa-custom-payloads.json` + golden examples | M | Hobby |
| DOC-7 | Link `IMPROVEMENT_PLAN.md` from README and ARCHITECTURE | S | Hobby |

### C.2 Backend structure (7 → 8)

| ID | Action | Effort | Tier |
|----|--------|--------|------|
| BE-1 | Audit `actions/db/queries.py`: every query includes `user_id` | S | Hobby |
| BE-2 | `confirm_transaction(user_id, tx_id)` — idempotent, status guard | S | Hobby |
| BE-3 | `session_start`: if user has pending tx in DB, set `confirmation_pending` + `last_transaction_id` | M | Hobby |
| BE-4 | Remove unused `litellm` dep from pyproject (if CLN-4 confirms) | S | Hobby |
| BE-5 | Structured mutation log fields (tx_id, user_id, action) — extend Loguru | S | Hobby |
| BE-6 | `backend/README.md`: uv, websockets override, docker commands | S | Hobby |
| BE-7 | Handler tests: `get_balance`, `delete_transaction`, `session_start`, `list_transactions`, `query_spending` | M | Testing |

### C.3 Frontend structure (7 → 8)

| ID | Action | Effort | Tier |
|----|--------|--------|------|
| FE-1 | Pin `next`, `react`, `react-dom` versions (no `latest`) | S | Hobby |
| FE-2 | Map Rasa `balance` / `spending_report` custom JSON → `ReportData` (not only client `computeReportData`) | M | Hobby |
| FE-3 | `persistChatMessage` → use returned row `id`; update React state | M | Hobby |
| FE-4 | Confirm/cancel buttons: disable from DB `transaction.status` | M | Hobby |
| FE-5 | Profile settings page: currency + timezone → `profiles` table | M | Hobby |
| FE-6 | Safer markdown rendering audit in `markdown.tsx` | S | Security |
| FE-7 | Optional: Zod parse Rasa payloads in `map-rasa-responses.ts` | M | Security |

### C.4 Integration completeness (4 → 8)

All items in **§B** plus:

| ID | Action | Effort | Tier |
|----|--------|--------|------|
| INT-10 | Playwright: login → send message → see assistant reply (mock Rasa or test env) | L | Scale |
| INT-11 | Staging Supabase project for CI smoke | M | Scale |

### C.5 Security (5 → 8)

| ID | Action | Effort | Tier |
|----|--------|--------|------|
| SEC-1 | Local: do not expose Rasa port publicly | S | Hobby |
| SEC-2 | Production: firewall Rasa to Next server IP only | S | Scale |
| SEC-3 | `RASA_WEBHOOK_SECRET` header checked by proxy or Next-only tunnel | M | Scale |
| SEC-4 | Tests: `/api/chat` returns 401 without session | S | Hobby |
| SEC-5 | Review `get_balance_summary` grants (service_role only) | S | Hobby |
| SEC-6 | Rate limit `/api/chat` (Vercel / Upstash) | M | Scale |
| SEC-7 | FE-6 / FE-7 — XSS and payload validation | M | Hobby |

**Hobby minimum:** SEC-1, SEC-4, SEC-5, FE-6.

### C.6 Testing (5 → 8)

| ID | Action | Effort | Tier |
|----|--------|--------|------|
| TST-1 | `.github/workflows/ci.yml` — frontend typecheck + vitest | S | Hobby |
| TST-2 | Same workflow — backend ruff + pyright + pytest | S | Hobby |
| TST-3 | BE-7 handler tests | M | Hobby |
| TST-4 | Golden files for Rasa webhook → `map-rasa-responses` | M | Hobby |
| TST-5 | Contract tests in CI (payload schema vs golden) | M | Hobby |
| TST-6 | Playwright in CI against staging | L | Scale |
| TST-7 | Optional: Supabase local + integration test for one query | L | Scale |

**Hobby minimum:** TST-1, TST-2, TST-3, TST-4.

### C.7 Ops / CI (3 → 7)

| ID | Action | Effort | Tier |
|----|--------|--------|------|
| OPS-1 | `ci.yml` (TST-1/2) | S | Hobby |
| OPS-2 | `scripts/smoke-e2e.sh` (INT-5) | M | Hobby |
| OPS-3 | Renovate or Dependabot for `frontend` + `backend/uv.lock` | S | Hobby |
| OPS-4 | Nightly/manual workflow for docker-smoke (secrets in GitHub) | M | Scale |
| OPS-5 | Health page or script: Rasa + actions + LiteLLM URLs | S | Hobby |
| OPS-6 | LiteLLM budget alert (email) | S | Scale |
| OPS-7 | sqlfluff or `supabase db lint` on migrations in CI | S | Hobby |

**Hobby minimum:** OPS-1, OPS-2, OPS-3, OPS-5.

---

## D. Features & product (hobby-valuable)

These are **user-visible** improvements that fit the simple stack.

| ID | Feature | Description | Effort | Scorecards |
|----|---------|-------------|--------|------------|
| FEAT-1 | **Profile on signup** | INT-2 migration | S | Integration |
| FEAT-2 | **Settings** | Currency + timezone (FE-5) | M | Frontend |
| FEAT-3 | **Accurate reports** | FE-2: server/Rasa numbers in report cards | M | Frontend, Integration |
| FEAT-4 | **Edit pending in UI** | Transaction card edits → send edit flow message to Rasa | M | Frontend |
| FEAT-5 | **Transaction list in chat** | Map `transaction_list` custom payload to rich UI | S | Frontend |
| FEAT-6 | **Forgot password** | Supabase reset password flow | S | Frontend |
| FEAT-7 | **Empty states** | No txs yet / Rasa loading / first-time hints | S | Frontend |
| FEAT-8 | **Export CSV** | Server route: user txs download | M | Frontend, Security |

Defer until later: bank import, multi-currency conversion, mobile app, notifications.

---

## E. Phased execution plan

### Phase 0 — Prove it works (1–2 weeks)

**Targets:** Integration 4→6, Ops 3→5

| Order | IDs |
|-------|-----|
| 1 | INT-1, INT-2 |
| 2 | INT-3, INT-4, INT-6 |
| 3 | INT-5, INT-8, OPS-2 |
| 4 | TST-1, TST-2, OPS-1 |
| 5 | DOC-1, DOC-7 |

**Done when:** Happy path works locally and is written in runbook + tracker.

---

### Phase 1 — Clean & align (1–2 weeks)

**Targets:** Frontend 7→8, Backend 7→8, Vision 8→9

| Order | IDs |
|-------|-----|
| 1 | CLN-6, CLN-7, CLN-8, CLN-9 |
| 2 | FE-3, FE-4, CLN-2, CLN-3, CLN-4, CLN-5 |
| 3 | BE-1, BE-2, BE-6 |
| 4 | DOC-3, DOC-6 |

---

### Phase 2 — Correct & safe (2–3 weeks)

**Targets:** Security 5→7, Testing 5→7

| Order | IDs |
|-------|-----|
| 1 | BE-3, BE-7, TST-3, TST-4, TST-5 |
| 2 | SEC-4, SEC-5, FE-6, FE-7 |
| 3 | FE-2, FEAT-3 |
| 4 | INT-7 |

---

### Phase 3 — Product polish (ongoing)

**Targets:** Frontend 8, Integration 7→8

| Order | IDs |
|-------|-----|
| 1 | FEAT-2, FEAT-4, FEAT-5, FEAT-7 |
| 2 | FE-1, FEAT-6 |
| 3 | FEAT-8 (optional) |

---

### Phase 4 — Scale when needed (defer)

Only when you deploy for others or run multiple Rasa instances:

| IDs |
|-----|
| DOC-2, DOC-4, SEC-2, SEC-3, SEC-6 |
| INT-10, INT-11, TST-6, OPS-4, OPS-6 |
| Redis tracker (`rasa/endpoints.yml`), Caddy TLS hardening |
| P2 from SYSTEM_DESIGN_REVIEW (rate limits, monitoring) |

---

## F. Master checklist (copy to tracker)

### Phase 0 — Prove

- [ ] INT-1 Migrations applied
- [ ] INT-2 Profile trigger
- [ ] INT-3 Docker up
- [ ] INT-4 Rasa train
- [ ] INT-5 smoke-e2e.sh
- [ ] INT-6 Runbook
- [ ] INT-8 RPC verified
- [ ] TST-1/2 CI
- [ ] OPS-1 CI merged
- [ ] DOC-1 local runbook

### Phase 1 — Clean

- [ ] CLN-6 DB-driven confirm UI
- [ ] CLN-7/8 Reset split
- [ ] CLN-9 Categories
- [ ] FE-3/4 Message ids + status
- [ ] BE-1/2 Query audit + idempotent confirm
- [ ] DOC-3 ADR service role

### Phase 2 — Safe

- [ ] BE-3 Slot sync from DB
- [ ] BE-7 + TST-3 Handler tests
- [ ] TST-4/5 Contract tests
- [ ] SEC-4/5 Auth + RPC grants
- [ ] FE-2 Reports from Rasa

### Phase 3 — Polish

- [ ] FEAT-2 Settings
- [ ] FEAT-4 Edit pending
- [ ] FE-1 Pin deps

### Phase 4 — Scale (later)

- [ ] SEC-2/3 Rasa network
- [ ] DOC-2 Deploy runbook
- [ ] Redis tracker

---

## G. Scorecard lift map (what moves the needle)

| To reach target | Minimum set of IDs |
|-----------------|-------------------|
| **Vision 9** | DOC-1, DOC-3, DOC-5, DOC-6, DOC-7, CLN-2 |
| **Backend 8** | BE-1, BE-2, BE-3, BE-6, BE-7 |
| **Frontend 8** | CLN-6, FE-2, FE-3, FE-4, FE-1, FEAT-2 |
| **Integration 8** | INT-1–8, INT-7, FEAT-1, smoke + happy path |
| **Security 8** | SEC-1–5, FE-6, FE-7, SEC-2/3/6 when public |
| **Testing 8** | TST-1–5, BE-7, INT-7 |
| **Ops 7** | OPS-1–3, OPS-5, OPS-2, INT-5 |

---

## H. What we explicitly will not do (hobby scope)

- Second NLU / OpenAI parse path (removed)
- DuckDB/SQLite as primary store
- Microservices split beyond existing Rasa/actions containers
- Full event-sourcing / `domain_events` table (unless debugging pain)
- Multi-tenant billing, teams, or roles beyond single user RLS

Revisit only if [ARCHITECTURE.md](./ARCHITECTURE.md) rules change.

---

## I. Maintaining this plan

1. Mark items done in **§F** and in `IMPLEMENTATION_TRACKER.md`.
2. Bump **Scorecard history** when a phase completes.
3. Add new rows under **§D Features** only if they fit the three-pillar stack.
4. Move items from Phase 4 → Phase 2 when you deploy publicly.

---

*Last updated: 2026-05-27 — aligned with legacy AI removal and [ARCHITECTURE.md](./ARCHITECTURE.md).*
