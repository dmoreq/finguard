# Roadmap and backlog

**Last updated:** 2026-05-28

This document tracks **planned** chat-backend and data-layer work.

- **Shipped:** [ARCHITECTURE.md](./ARCHITECTURE.md)
- **Target design:** [design/chat-backend-target.md](./design/chat-backend-target.md)
- **Decisions:** [ADR-003](./decisions/003-low-cost-chat-backend.md), [ADR-004](./decisions/004-chat-backend-evolution.md)
- **Implementation log:** [plans/P1-P2-implementation-plan.md](./plans/P1-P2-implementation-plan.md)
- **Product priorities:** [PRODUCT_PLAN.md](./PRODUCT_PLAN.md)
- **Use case catalog:** [USE_CASE_CATALOG.md](./USE_CASE_CATALOG.md)
- **Feature specs (RFCs):** [specs/README.md](./specs/README.md) — one file per feature for build/defer/reject review

---

## Shipped (P1 + P2, 2026-05-28)

| Item | Status |
|------|--------|
| Semantic Router + hybrid fallback (`ROUTER_MODE`) | **Done** |
| Pending guard before primary router | **Done** |
| Gemini JSON extraction, rules-first (`LLM_EXTRACT_ENABLED`) | **Done** |
| Optional `description` in extract schema | **Done** |
| SQLite `chat_sessions` persistence | **Done** |

---

## Prioritized backlog

| Priority | Item | Layer | Status | When to do it |
|----------|------|-------|--------|----------------|
| **P3** | **Burr** FSM (replace or wrap `dialogue/engine.py`) | 2 | **Backlog** | New flows make dialogue handlers hard to maintain |
| **P4** | **DuckDB** analytics on SQLite file | 4 | **Backlog** | Report queries are slow or analytics need columnar SQL |
| — | Burr local UI / transition debugging in runbook | 2 | Backlog | When Burr (P3) starts |
| — | Local LLM via vLLM | 3 | Backlog | Optional; after cloud extract is stable |
| — | Outlines library (replace raw Gemini JSON) | 3 | Backlog | Optional; current Gemini structured JSON meets P2 |

### Non-goals (unless requirements change)

- LangGraph / tool-calling agents for money flows
- LLM-generated report prose (templates + SQL only)
- DuckDB in the same change set as unrelated features
- Mandatory LLM on every expense message while rules succeed

---

## Burr (backlog detail)

**Goal:** Explicit, inspectable dialogue graph for multi-turn flows (collect → pending → confirm / discard / edit).

**Why deferred:** `DialogueEngine` + focused handlers already implement core flows with tests and no new dependency.

**Triggers to start Burr work:**

- Adding a 7th distinct dialogue flow (e.g. budgets, splits, recurring)
- Confirm/edit branching becomes error-prone to change across handlers
- Team wants Burr UI for transition debugging in local dev

**Scope when started:**

- Port handlers to a Burr graph; keep `services/*` unchanged
- Preserve [chat-payloads.json](./schemas/chat-payloads.json)

---

## DuckDB (backlog detail)

**Goal:** Fast columnar aggregations for spending reports by querying the SQLite database file.

**Why deferred:** Personal-scale SQLite + service SQL is sufficient today.

**Triggers:** Profiling shows slow report endpoints; cross-user analytics needs.

**Scope:** Read-only DuckDB on `finguard.db`; writes stay SQLite; template responses only.

---

## Success metrics

| Item | Gate |
|------|------|
| Semantic Router | ≥95% on `utterances.jsonl` with `ROUTER_MODE=hybrid` locally; CI uses `ROUTER_MODE=keyword` + mocks |
| LLM extract | Off by default; on only when rules leave gaps |
| Sessions | Pending flow survives backend restart (see `test_session_persist.py`) |
