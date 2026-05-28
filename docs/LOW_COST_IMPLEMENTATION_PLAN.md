# Low-Cost Backend — Comprehensive Implementation Plan

**Status:** Approved for execution
**Date:** 2026-05-28
**Parent spec:** [low_cost_plan.md](./low_cost_plan.md)
**Goal:** Replace Rasa CALM + Rasa Pro with Semantic Router + Burr + Instructor, reuse SQLite/handlers, and **remove all Rasa CALM code, tooling, and documentation** from the active codebase.

---

## Table of contents

1. [Objectives and non-goals](#1-objectives-and-non-goals)
2. [Current state](#2-current-state)
3. [Target architecture](#3-target-architecture)
4. [Repository layout (after migration)](#4-repository-layout-after-migration)
5. [Design decisions](#5-design-decisions)
6. [Implementation phases](#6-implementation-phases)
7. [Rasa CALM decommission checklist](#7-rasa-calm-decommission-checklist)
8. [Handler refactor plan](#8-handler-refactor-plan)
9. [Frontend and API contract](#9-frontend-and-api-contract)
10. [Testing and CI](#10-testing-and-ci)
11. [Documentation updates](#11-documentation-updates)
12. [Risks, rollback, and verification gates](#12-risks-rollback-and-verification-gates)
13. [Effort estimate](#13-effort-estimate)
14. [Commit strategy](#14-commit-strategy)

---

## 1. Objectives and non-goals

### Objectives

| # | Objective | Done when |
|---|-----------|-----------|
| O1 | Chat works **without** `RASA_PRO_LICENSE`, Docker `rasa/rasa-pro`, or `mock-rasa.py` | `make dev` → full record/confirm/report flows |
| O2 | **Deterministic** dialogue (Burr FSM); LLM only for structured extraction | Token logs show LLM only on extract nodes |
| O3 | **Reuse** SQLite schema, queries, and business rules | No duplicate INSERT/report SQL |
| O4 | **Preserve** UI contract (`transaction_pending`, `balance`, `spending_report`) | Golden fixture tests pass unchanged |
| O5 | **Delete** Rasa CALM artifacts from repo and CI | Grep for `rasa` in active code/docs ≈ zero (archive allowed) |

### Non-goals (this migration)

- Supabase / auth reintroduction
- Multi-user production deploy hardening (keep ADR-002 patterns, rename later)
- DuckDB analytics (defer unless SQL perf requires it)
- LLM-generated natural language for reports (keep templates)
- Mobile / native clients

---

## 2. Current state

### Runtime today

```text
Browser → Next.js POST /api/chat
              → RASA_URL :5005 (Docker Rasa Pro OR mock-rasa.py)
                    → CALM flows → action webhook → :5055/webhook
              → Next.js GET /api/data/* → :5055/data/*
```

### Feature parity map (Rasa → new stack)

| Rasa flow / behavior | Source file | New owner |
|----------------------|-------------|-----------|
| `record_expense` / `record_income` | `record_transaction.yml` | Burr `collecting` + Instructor + `record_transaction` service |
| `confirm_pending_transaction` | `manage_pending.yml` | Burr `awaiting_confirmation` + router bias + `update_transaction` service |
| `discard_pending_transaction` | `manage_pending.yml` | Burr + `delete_transaction` service |
| `edit_pending_transaction` | `manage_pending.yml` | Burr + partial Instructor + `update_transaction` service |
| `get_balance` | `query_spending.yml` | Router + rule-based period parse + `get_balance` service |
| `query_spending_report` | `query_spending.yml` | Router + period/category parse + `query_spending` service |
| `list_recent_transactions` | `query_spending.yml` | Router + `list_transactions` service |
| `no_pending_transaction` | `manage_pending.yml` | Burr guard + template response |
| Session profile slots | `session_start.py` | Load profile in chat session init (no Rasa slot events) |

### Pain points driving migration

- CALM requires **Rasa Pro** license for real flows; mock is stub-only.
- Two runtimes (Rasa + action server) and **LiteLLM** mainly for Rasa’s LLM calls.
- CI e2e blocked on `secrets.RASA_PRO_LICENSE`.
- `rasa-sdk` couples business logic to `Tracker` / `CollectingDispatcher`.

---

## 3. Target architecture

### Runtime after migration

```text
Browser → Next.js POST /api/chat
              → BACKEND_URL :5055/webhooks/rest/webhook  (same JSON as Rasa REST)
                    Layer 1 Semantic Router (local embeddings)
                    Layer 2 Burr FSM (session state in memory/SQLite)
                    Layer 3 Instructor (extract only)
                    Layer 4 Services → SQLite
              → Next.js /api/data/* → :5055/data/*  (unchanged)
```

**Single Python process** (`uvicorn actions.server:app`) serves chat webhook + data API. No port `:5005`, no Docker Rasa, no `mock-rasa.py`.

### Layer responsibilities

| Layer | Package | Input | Output |
|-------|---------|-------|--------|
| 1 | `actions.chat.router` | User text + session flags | `Intent` enum + confidence |
| 2 | `actions.chat.fsm` | Intent + state | Next node, prompts, service calls |
| 3 | `actions.chat.extract` | Utterance + schema | `ExpenseDetail` / `IncomeDetail` / `EditFields` |
| 4 | `actions.services.*` | Typed DTOs | DB rows + `ChatPayload` list |

### Session state

| Field | Storage | Notes |
|-------|---------|-------|
| `user_id` | Per request | From Next.js `metadata.user_id` |
| `dialogue_phase` | Burr state | `idle` \| `collecting` \| `awaiting_confirmation` |
| `partial_transaction` | Burr state | Merge with extraction |
| `last_transaction_id` | Burr state + SQLite | Must match pending row |
| `confirmation_pending` | Burr state | When true, router prefers `manage_pending` |
| `chat_history` | Burr state (last N) | Optional context for extraction |

**Persistence:** In-memory per `sender` for v1 (same as Rasa tracker in dev). Optional `chat_sessions` SQLite table in a follow-up if you need survive-restart sessions.

### LLM configuration

| Environment | Model path |
|-------------|------------|
| Dev (no key) | Skip extraction; return “please specify amount and category” templates |
| Dev (Ollama) | `OLLAMA_BASE_URL` + small model via Instructor-compatible client |
| Prod / dev cloud | `GEMINI_API_KEY` → Gemini Flash class via Instructor |

**LiteLLM:** Remove from default `make dev`. Keep as **optional** dev dependency only if you want one proxy for multiple providers later—not required for v1.

---

## 4. Repository layout (after migration)

```text
backend/
  actions/
    server.py                 # FastAPI: /health, /data/*, /webhooks/rest/webhook
    chat/
      __init__.py
      router.py               # Semantic Router setup + classify()
      routes.py               # Route definitions + utterance examples
      fsm/
        app.py                # Burr ApplicationBuilder graph
        state.py              # SessionState TypedDict / Pydantic
        nodes.py              # @action nodes
      extract/
        models.py             # Pydantic extraction schemas
        client.py             # Instructor client factory
      respond/
        payloads.py             # Build Rasa-shaped json_message dicts
        templates.py            # Static utterances
      session.py                # Load/store session by sender_id
    services/                 # Pure async functions (no rasa-sdk)
      record_transaction.py
      update_transaction.py
      delete_transaction.py
      get_balance.py
      query_spending.py
      list_transactions.py
      profile.py
    handlers/                 # DELETED after services cutover (Phase 8)
    db/                       # unchanged
    models/
    utils/
  tests/
    test_chat/                # router, fsm, extract, webhook contract
    test_services/            # moved/refactored handler tests
  pyproject.toml              # burr, semantic-router, instructor; no rasa-sdk
  # REMOVED: rasa/, litellm/, docker-compose.yml (or empty stub)
```

---

## 5. Design decisions

Record as **ADR-003** when Phase 1 starts ([decisions/003-low-cost-chat-backend.md](./decisions/003-low-cost-chat-backend.md)).

| ID | Decision | Rationale |
|----|----------|-----------|
| D1 | **Webhook-compatible** `POST /webhooks/rest/webhook` on action server | Zero UI churn; same payload as Rasa REST |
| D2 | **Services layer** under `actions/services/` | Removes `rasa-sdk`; handlers were thin wrappers anyway |
| D3 | **Burr** for FSM | Explicit graph > nested ifs; matches CALM flow YAML mentally |
| D4 | **Semantic Router** for intent | $0 routing; tune with utterance bank |
| D5 | **Instructor** for extraction | Retries + Pydantic; one LLM call per extract step |
| D6 | **Unified port 5055** | One `make dev` process; drop `:5005` |
| D7 | Rename env `RASA_URL` → `CHAT_BACKEND_URL` (alias both during transition) | Honest naming; keep backward compat 1 release |

---

## 6. Implementation phases

Each phase ends with **verification gate** (Section 12). Do not start the next phase until the gate passes.

---

### Phase 0 — Spike and fixtures (2–3 days)

**Purpose:** De-risk router accuracy and Burr ergonomics before deleting Rasa.

| Task | Details |
|------|---------|
| 0.1 | Create `backend/tests/fixtures/utterances.jsonl` — ≥50 lines: intent label + text (EN + VN amounts, confirm/discard phrases) |
| 0.2 | Spike script `backend/scripts/spike_router.py` — print top-1 route + score; target ≥90% on fixture set |
| 0.3 | Spike `backend/scripts/spike_burr.py` — minimal graph: idle → collecting → awaiting_confirmation |
| 0.4 | Draft ADR-003 | Lock D1–D7 |

**Deliverables:** Spike scripts (can live under `scripts/` or `backend/scripts/`), utterance bank, ADR-003.

**Gate:** ≥85% route accuracy on fixture set; team agrees Burr graph is readable.

---

### Phase 1 — Scaffold chat package (1–2 days)

| Task | Details |
|------|---------|
| 1.1 | Add deps to `pyproject.toml`: `semantic-router`, `burr`, `instructor`, `sentence-transformers` (or encoder dep per semantic-router docs) |
| 1.2 | Create `actions/chat/` package skeleton per Section 4 |
| 1.3 | `actions/chat/session.py` — in-memory dict keyed by `sender_id` |
| 1.4 | `actions/chat/respond/payloads.py` — functions mirroring [schemas/rasa-custom-payloads.json](./schemas/rasa-custom-payloads.json) |
| 1.5 | Stub `POST /webhooks/rest/webhook` returning fixed `text-only` payload |

**Gate:** `curl` stub webhook returns 200; pytest `test_webhook_stub`.

---

### Phase 2 — Services layer (3–4 days)

Extract business logic from `rasa-sdk` handlers into testable services.

| Task | From | To |
|------|------|-----|
| 2.1 | `handlers/record_transaction.py` | `services/record_transaction.py` — `async def record(...)-> list[ChatPayload]` |
| 2.2 | `handlers/update_transaction.py` | `services/update_transaction.py` |
| 2.3 | `handlers/delete_transaction.py` | `services/delete_transaction.py` |
| 2.4 | `handlers/get_balance.py` | `services/get_balance.py` |
| 2.5 | `handlers/query_spending.py` | `services/query_spending.py` |
| 2.6 | `handlers/list_transactions.py` | `services/list_transactions.py` |
| 2.7 | Profile load | `services/profile.py` — wrap `get_profile` for currency/timezone |
| 2.8 | Port tests | `tests/test_handlers/*` → `tests/test_services/*` (same assertions, no Tracker mocks) |

**Rules:**

- Services take **Pydantic input models**, return **`list[dict]`** webhook-shaped payloads (not `CollectingDispatcher`).
- No `SlotSet` events — return updated session fields from FSM instead.

**Gate:** `uv run pytest tests/test_services/ -q` green; handlers still pass (thin delegates) until Phase 8.

---

### Phase 3 — Semantic Router (2 days)

| Task | Details |
|------|---------|
| 3.1 | `actions/chat/routes.py` — define `Route` list: `log_expense`, `log_income`, `check_balance`, `analyze_spending`, `list_transactions`, `manage_pending`, `chitchat`, `unknown` |
| 3.2 | `actions/chat/router.py` — `classify(text, *, confirmation_pending: bool) -> IntentResult` |
| 3.3 | When `confirmation_pending`, boost `manage_pending` or bypass router for regex `^(yes|confirm|ok|discard|cancel|no)\b` |
| 3.4 | Tests: `tests/test_chat/test_router.py` against `utterances.jsonl` |

**Gate:** Router tests ≥85% accuracy; failures documented with planned utterance additions.

---

### Phase 4 — Instructor extraction (2–3 days)

| Task | Details |
|------|---------|
| 4.1 | `extract/models.py` — `TransactionExtract`, `PeriodExtract`, `EditPendingExtract` |
| 4.2 | `extract/client.py` — `get_extractor()`; no-op when `GEMINI_API_KEY` unset |
| 4.3 | `extract/period.py` — **rule-first** parser for `this_month`, `last_7d`, etc. (avoid LLM for reports) |
| 4.4 | Max retries = 2, timeout 30s |
| 4.5 | Tests with mocked LLM (`pytest-httpx` or instructor mock) |

**Gate:** Extraction tests pass; invalid amount triggers retry then user-facing error template.

---

### Phase 5 — Burr FSM (5–7 days)

Core migration — port YAML flow logic to explicit graph.

| Task | Details |
|------|---------|
| 5.1 | `fsm/state.py` — session model |
| 5.2 | `fsm/nodes.py` — `route_input`, `collect_fields`, `extract_llm`, `validate`, `record_pending`, `await_confirm`, `confirm`, `discard`, `edit_pending`, `report_balance`, `report_spending`, `list_txns`, `chitchat`, `unknown` |
| 5.3 | `fsm/app.py` — transitions with `when(...)` |
| 5.4 | Wire nodes → `services.*` |
| 5.5 | Multi-turn collecting: merge `partial_transaction`, ask template for first missing required field |
| 5.6 | Rejection: `amount <= 0` → template ask (no LLM) |
| 5.7 | `chat/webhook.py` — `handle_message(sender, text, metadata)` orchestrates router + burr.run + payload flatten |

**Parity checklist (must all pass):**

- [ ] Record expense → pending card payload
- [ ] Record income → pending card payload
- [ ] Confirm → status `confirmed` in SQLite
- [ ] Discard → row removed or marked discarded per current behavior
- [ ] Edit amount on pending → updated card
- [ ] Balance report → `balance` payload
- [ ] Spending report → `spending_report` payload
- [ ] List transactions → text or structured per current UI
- [ ] Confirm with no pending → helpful error text

**Gate:** `tests/test_chat/test_fsm_integration.py` covering full multi-turn scripts; manual smoke via curl.

---

### Phase 6 — Wire FastAPI + dev tooling (1–2 days)

| Task | Details |
|------|---------|
| 6.1 | Add `POST /webhooks/rest/webhook` to `actions/server.py` — delegate to `chat.webhook.handle_message` |
| 6.2 | Remove `POST /webhook` (Rasa action callback) and `ActionExecutor` / `rasa-sdk` registration |
| 6.3 | Update `scripts/dev-lite.sh` — only uvicorn :5055 + Next (no Docker, mock, LiteLLM) |
| 6.4 | Update `Makefile`: remove `train`; `dev` = actions + frontend; `health` checks :5055 webhook |
| 6.5 | Update `scripts/check-health.sh`, `ensure-local-backend.sh`, `playwright-webserver.sh`, `integration-chat.sh`, `smoke-e2e.sh` |
| 6.6 | `backend/.env.example` — remove `RASA_PRO_LICENSE`; document `GEMINI_API_KEY`, `CHAT_BACKEND_URL` |

**Gate:** `make dev` → chat record + confirm works in browser; `make smoke` green.

---

### Phase 7 — Frontend alignment (1 day)

| Task | Details |
|------|---------|
| 7.1 | `frontend/.env.example` — `CHAT_BACKEND_URL=http://localhost:5055` (keep `RASA_URL` as deprecated alias reading same var) |
| 7.2 | `resolve-user.ts` — `getChatBackendUrl()` with fallback `RASA_URL` |
| 7.3 | `route.ts` — error codes `CHAT_NOT_CONFIGURED`, `CHAT_UNAVAILABLE` (map old codes in tests for one PR or breaking rename) |
| 7.4 | Optional rename: `map-rasa-responses.ts` → `map-chat-responses.ts` (re-export alias) |
| 7.5 | Update Playwright / integration scripts to :5055 |

**Gate:** `pnpm test` + `test-e2e` green; golden fixtures unchanged on disk.

---

### Phase 8 — Rasa CALM decommission (2 days)

Execute [Section 7](#7-rasa-calm-decommission-checklist) in order.

**Gate:** `rg -i 'rasa|calm' --glob '!docs/archive/**' --glob '!*.lock'` returns only transitional aliases (if any), ADR-002 archive note, and changelog entries.

---

### Phase 9 — Tests and CI (2–3 days)

| Task | Details |
|------|---------|
| 9.1 | Delete `tests/test_mock_rasa.py` |
| 9.2 | Add `tests/test_chat/test_webhook_contract.py` — load golden JSON from `frontend/.../fixtures/` |
| 9.3 | Port `test_confirm_flow_integration.py` to service + FSM level |
| 9.4 | Update [TEST_STRATEGY.md](./TEST_STRATEGY.md) — remove Rasa e2e section; add chat layer matrix |
| 9.5 | Remove `.github/workflows/rasa-e2e.yml` |
| 9.6 | Ensure root `ci.yml` runs `pytest` + Vitest only |

**Gate:** CI green without secrets; coverage on `actions/chat` and `actions/services` ≥ same critical paths as before.

---

### Phase 10 — Documentation and ADR cleanup (1 day)

Execute [Section 11](#11-documentation-updates).

**Gate:** README quick start has no `make train`, no Rasa license mention.

---

## 7. Rasa CALM decommission checklist

Use this as a literal tick list during **Phase 8**.

### 7.1 Delete — code and config

| Path | Reason |
|------|--------|
| `backend/rasa/` (entire tree) | CALM flows, domain, e2e tests |
| `scripts/mock-rasa.py` | Replaced by native webhook |
| `scripts/train-lite.sh` | Rasa train |
| `scripts/rasa-e2e-docker.sh` | Rasa e2e |
| `backend/docker-compose.yml` | Rasa Pro container |
| `backend/litellm/config.yaml` | Rasa LLM routing (optional delete if unused) |
| `backend/actions/handlers/` | After services + FSM cutover |
| `backend/tests/test_mock_rasa.py` | Mock server tests |
| `.github/workflows/rasa-e2e.yml` | Pro license CI |
| `.gitignore` entries | `backend/rasa/models/`, `backend/.rasa_cache/` — remove if dirs gone |
| Root `/rasa/` gitignore | HF cache — keep ignore pattern or delete line |

### 7.2 Delete — dependencies

| Location | Remove |
|----------|--------|
| `backend/pyproject.toml` | `rasa-sdk` |
| `backend/pyproject.toml` dev | `litellm`, `backoff` if only used for Rasa train/LiteLLM |

Run `cd backend && uv lock && uv sync` after edits.

### 7.3 Modify — scripts and Makefile

| Path | Change |
|------|--------|
| `Makefile` | Remove `train` target; update `dev`, `down`, `health`, `smoke`, `setup` help text |
| `scripts/dev-lite.sh` | Single uvicorn; no Docker/mock/LiteLLM |
| `scripts/smoke-e2e.sh` | Hit `/webhooks/rest/webhook` on :5055 |
| `scripts/integration-chat.sh` | `CHAT_BACKEND_URL` / :5055 |
| `scripts/playwright-webserver.sh` | Drop mock-rasa spawn |
| `scripts/check-health.sh` | Remove :5005 Rasa check |
| `scripts/ensure-local-backend.sh` | Align with unified backend |
| `backend/scripts/verify-stack.sh` | Remove Rasa steps |

### 7.4 Modify — backend application

| Path | Change |
|------|--------|
| `backend/actions/server.py` | Remove `ActionExecutor`, `/webhook`; add REST chat webhook |
| `backend/actions/__init__.py` | Drop CALM references |
| `backend/pyproject.toml` | Description, deps |
| `backend/README.md` | New architecture |
| `backend/.env.example` | Remove license keys |
| `backend/pyrightconfig.json` | Drop `rasa` paths if present |

### 7.5 Modify — frontend

| Path | Change |
|------|--------|
| `frontend/src/app/api/chat/route.ts` | `CHAT_BACKEND_URL`, error codes |
| `frontend/src/server/chat/resolve-user.ts` | Rename helpers |
| `frontend/src/server/chat/*.test.ts` | Env var names |
| `frontend/src/server/chat/fixtures/text-only-webhook.json` | Remove “Mock Rasa” copy |
| `frontend/.env.example` | `CHAT_BACKEND_URL` |
| `frontend/src/app/settings/page.tsx` | “Used by assistant” not “Rasa” |

### 7.6 Modify — docs (active, not archive)

| Path | Change |
|------|--------|
| [ARCHITECTURE.md](./ARCHITECTURE.md) | Rewrite for 4-layer chat on :5055 |
| [IMPLEMENTATION_TRACKER.md](./IMPLEMENTATION_TRACKER.md) | New milestones or archive file |
| [TEST_STRATEGY.md](./TEST_STRATEGY.md) | Remove Rasa CALM e2e |
| [runbooks/local-development.md](./runbooks/local-development.md) | No Docker Rasa, no train |
| [runbooks/production-deploy.md](./runbooks/production-deploy.md) | Chat backend private network |
| [README.md](../README.md) | Stack diagram |
| [CLEANUP_PLAN.md](./CLEANUP_PLAN.md) | Add “Rasa CALM cleanup” section executed |
| [low_cost_plan.md](./low_cost_plan.md) | Link to this plan; status → implemented |

### 7.7 Archive — do not delete (historical)

Move or leave in `docs/archive/` with header **“Superseded — pre low-cost migration”**:

| Path | Action |
|------|--------|
| `docs/archive/rasa-calm-backend-plan.md` | Already archived; add superseded banner |
| `docs/decisions/002-rasa-network-trust.md` | Supersede → `003-low-cost-chat-backend.md` (rename trust boundary to chat backend) |
| `docs/decisions/001-service-role-in-actions.md` | Keep (Supabase future) |

### 7.8 Rename — schemas (optional but recommended)

| From | To |
|------|-----|
| `docs/schemas/rasa-custom-payloads.json` | `docs/schemas/chat-payloads.json` |
| References in tests/docs | Update imports and paths |

Keep a one-release re-export or symlink only if external tools reference old path.

---

## 8. Handler refactor plan

### Before (Rasa handler)

```python
class ActionRecordTransaction(Action):
    async def run(self, dispatcher, tracker, domain):
        slots = RecordTransactionSlots(amount=tracker.get_slot("amount"), ...)
        ...
        dispatcher.utter_message(json_message=payload)
        return [SlotSet("confirmation_pending", True), ...]
```

### After (service + FSM)

```python
# actions/services/record_transaction.py
async def record_transaction(input: RecordInput) -> ServiceResult:
    """Returns payloads + session_updates."""
    ...

# actions/chat/fsm/nodes.py
@action(...)
def record_pending(state: SessionState, ...) -> tuple[SessionState, list[dict]]:
    result = await record_transaction(...)
    return state.update(confirmation_pending=True, ...), result.payloads
```

### `ServiceResult` shape

```python
class ServiceResult(BaseModel):
    payloads: list[dict]           # webhook messages
    session: SessionUpdates | None # fields for Burr state merge
```

### Handler removal order

1. Implement service + tests.
2. Point Burr node to service.
3. Delete handler module.
4. Remove from `ActionExecutor` (then delete executor entirely in Phase 6).

### `session_start.py`

Replace with: on first message from `sender`, load profile from SQLite into Burr state (`user_currency`, `user_timezone`). No Rasa session event.

---

## 9. Frontend and API contract

### Request (unchanged)

```http
POST /webhooks/rest/webhook
Content-Type: application/json

{
  "sender": "<userId>",
  "message": "<text>",
  "metadata": { "user_id": "<userId>" }
}
```

### Response (unchanged)

Array of `{ "text"?: string, "custom"?: object, "json_message"?: object }` — prefer `custom` matching [chat-payloads](./schemas/rasa-custom-payloads.json).

### Next.js BFF

- Continue validating with `parseChatRequest`.
- Map responses through `mapRasaWebhookToChatResponse` until renamed.
- Rate limit unchanged.

### Environment variables

| Variable | Purpose | Default |
|----------|---------|---------|
| `CHAT_BACKEND_URL` | Server-side chat backend base URL | `http://127.0.0.1:5055` |
| `RASA_URL` | **Deprecated** alias | Read if `CHAT_BACKEND_URL` unset |
| `GEMINI_API_KEY` | Instructor extraction | optional in dev |
| `ACTIONS_URL` | Frontend data API | `http://127.0.0.1:5055` |

---

## 10. Testing and CI

### Test pyramid (post-migration)

| Layer | Location | Examples |
|-------|----------|----------|
| Router unit | `tests/test_chat/test_router.py` | utterance bank |
| Extract unit | `tests/test_chat/test_extract.py` | mocked LLM |
| FSM integration | `tests/test_chat/test_fsm_*.py` | multi-turn scripts |
| Service unit | `tests/test_services/` | DB + payloads |
| Webhook contract | `tests/test_chat/test_webhook_contract.py` | golden fixtures |
| Frontend map | `map-rasa-contract.test.ts` | unchanged JSON files |
| Playwright | `frontend/e2e/` | record → confirm → sidebar |

### CI workflow (target)

```yaml
# .github/workflows/ci.yml (conceptual)
- backend: uv run pytest tests/ -q
- frontend: pnpm test && pnpm typecheck
# No rasa-e2e.yml
```

### Burr local UI (dev-only)

Document in runbook: `burr-test-case` / Burr UI for debugging transitions during Phase 5.

---

## 11. Documentation updates

| Document | Action |
|----------|--------|
| [ARCHITECTURE.md](./ARCHITECTURE.md) | Replace Rasa diagram with 4-layer diagram from [low_cost_plan.md](./low_cost_plan.md) |
| [IMPLEMENTATION_TRACKER.md](./IMPLEMENTATION_TRACKER.md) | Archive or replace with milestone table from this plan |
| [TEST_STRATEGY.md](./TEST_STRATEGY.md) | Chat/backend matrix; delete Rasa Pro e2e |
| [low_cost_plan.md](./low_cost_plan.md) | Status: **Implemented** (link here) |
| [CLEANUP_PLAN.md](./CLEANUP_PLAN.md) | Section 5: Rasa CALM removal executed |
| [decisions/003-low-cost-chat-backend.md](./decisions/003-low-cost-chat-backend.md) | **Create** — D1–D7 |
| [decisions/002-rasa-network-trust.md](./decisions/002-rasa-network-trust.md) | Status → **Superseded by ADR-003** |
| [backend/README.md](../backend/README.md) | Dev without Docker |
| [README.md](../README.md) | Remove `make train`, license |
| [runbooks/local-development.md](./runbooks/local-development.md) | Single backend process |
| [runbooks/production-deploy.md](./runbooks/production-deploy.md) | Chat backend private; no Rasa ports |

---

## 12. Risks, rollback, and verification gates

### Risks

| Risk | Mitigation |
|------|------------|
| Router misclassification | Utterance bank + pending-state override + logging |
| FSM parity bugs | Port e2e scenarios from `backend/rasa/tests/flows/*.yml` to pytest scripts |
| Session loss on restart | Document as known; add SQLite session table if needed |
| Embedding model download size | Pin model; document first-run download in README |
| Scope creep (DuckDB, agents) | Defer per non-goals |

### Rollback

Until Phase 8 completes, keep migration branch. If rollback needed:

1. Restore `backend/rasa/` and `mock-rasa.py` from git.
2. Revert `server.py` to dual webhook mode.
3. Restore `dev-lite.sh` and Docker compose.

After Phase 8, rollback = revert merge commit; no partial Rasa without restoring from git history.

### Global verification (definition of done)

```bash
# From repo root
make install
make dev
# Manual: record expense → pending → confirm → appears in sidebar
# Manual: "what's my balance this month"

make test
make smoke
cd frontend && pnpm test:e2e   # if Playwright installed

rg -i 'rasa|calm' --glob '!docs/archive/**' --glob '!uv.lock' --glob '!pnpm-lock.yaml'
# Expected: no matches in code; only optional deprecated env alias docs
```

---

## 13. Effort estimate

| Phase | Days (focused) |
|-------|----------------|
| 0 Spike | 2–3 |
| 1 Scaffold | 1–2 |
| 2 Services | 3–4 |
| 3 Router | 2 |
| 4 Extract | 2–3 |
| 5 FSM | 5–7 |
| 6 Wire + dev | 1–2 |
| 7 Frontend | 1 |
| 8 Decommission | 2 |
| 9 Tests/CI | 2–3 |
| 10 Docs | 1 |
| **Total** | **~22–30 days** (one engineer, part-time → 4–6 weeks) |

Parallelization: Phase 2 (services) can overlap late Phase 0; Phase 7 can wait until Phase 6.

---

## 14. Commit strategy

Atomic commits per phase (or sub-phase), conventional messages:

```text
feat(backend): add chat package scaffold and stub webhook
feat(backend): extract record_transaction into services layer
feat(backend): add semantic router and utterance tests
feat(backend): add instructor extraction with period rules
feat(backend): implement Burr FSM for record and confirm flows
feat(backend): wire REST webhook and simplify dev-lite
refactor(frontend): CHAT_BACKEND_URL with RASA_URL fallback
chore: remove Rasa CALM docker, flows, and mock server
test: add chat webhook contract and FSM integration tests
docs: rewrite architecture for low-cost backend
```

**Do not** mix “add Burr FSM” and “delete backend/rasa” in one commit — reviewers need a green midpoint where services exist before Rasa deletion.

---

## Related documents

- [low_cost_plan.md](./low_cost_plan.md) — architecture rationale and review
- [TEST_STRATEGY.md](./TEST_STRATEGY.md) — update during Phase 9
- [schemas/rasa-custom-payloads.json](./schemas/rasa-custom-payloads.json) — contract to preserve (rename optional)

---

## Document history

| Date | Change |
|------|--------|
| 2026-05-28 | Initial comprehensive implementation plan |
