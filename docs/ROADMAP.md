# Roadmap and backlog

**Last updated:** 2026-05-28

This document tracks **planned** chat-backend and data-layer work.

- **Shipped:** [ARCHITECTURE.md](./ARCHITECTURE.md)
- **Target design:** [design/chat-backend-target.md](./design/chat-backend-target.md)
- **Decisions:** [ADR-003](./decisions/003-low-cost-chat-backend.md), [ADR-004](./decisions/004-chat-backend-evolution.md)

---

## Prioritized backlog

Work in **priority order**. Do not start a lower item until the trigger in the “When” column is met (or the team explicitly reprioritizes).

| Priority | Item | Layer | Status | When to do it |
|----------|------|-------|--------|----------------|
| **P1** | **Semantic Router** (local embeddings, thresholds, `unknown` bucket) | 1 | Backlog | Keyword router misses real utterances; golden set accuracy below target |
| **P1** | Router override while `confirmation_pending` | 1 | Backlog | Ship with semantic router — never misroute `yes` / `discard` / edits |
| **P2** | **Outlines + Gemini** extraction (rules-first fallback) | 3 | Backlog | Rules often leave incomplete `partial_transaction` after one turn |
| **P2** | Optional `description` in extraction schema; require amount + category | 3 | Backlog | With Outlines (or any LLM extract) |
| **P2** | Persist chat sessions (SQLite `chat_sessions` or equivalent) | 2 | Backlog | Restarts or multi-instance deploy break in-memory sessions |
| **P3** | **Burr** FSM (replace or wrap `engine.py`) | 2 | **Backlog** | New flows make `engine.py` hard to maintain (see triggers below) |
| **P4** | **DuckDB** analytics on SQLite file | 4 | **Backlog** | Report queries are slow or analytics need columnar SQL |
| — | Burr local UI / transition debugging in runbook | 2 | Backlog | When Burr (P3) starts |
| — | Local LLM via Outlines + vLLM | 3 | Backlog | Optional; after cloud extract is stable |

### Non-goals (unless requirements change)

- LangGraph / tool-calling agents for money flows
- LLM-generated report prose (templates + SQL only)
- DuckDB in the same change set as semantic routing or Outlines
- Mandatory LLM on every expense message while rules succeed

---

## Burr (backlog detail)

**Goal:** Explicit, inspectable dialogue graph for multi-turn flows (collect → pending → confirm / discard / edit).

**Why deferred:** The shipped `engine.py` FSM already implements the core FinGuard flows with simpler tests and no new dependency.

**Triggers to start Burr work:**

- Adding a 7th distinct dialogue flow (e.g. budgets, splits, recurring)
- Confirm/edit branching becomes error-prone to change in one file
- Team wants Burr UI for transition debugging in local dev

**Scope when started:**

- Port `idle` → `collecting` → `awaiting_confirmation` → actions to a Burr graph
- Keep service layer unchanged (`backend/actions/services/`)
- Preserve [chat-payloads.json](./schemas/chat-payloads.json) webhook contract
- Integration tests for multi-turn scripts (replace or extend `tests/test_chat/`)

**References:** [design/chat-backend-target.md](./design/chat-backend-target.md) Layer 2; [archive/low-cost-migration/implementation-plan.md](./archive/low-cost-migration/implementation-plan.md) Phase 5 (historical).

---

## DuckDB (backlog detail)

**Goal:** Fast columnar aggregations for spending reports by querying the SQLite database file (OLAP on OLTP data).

**Why deferred:** Personal-scale SQLite + Python/SQL in services is sufficient today; adds dependency and ops surface without proven pain.

**Triggers to start DuckDB work:**

- Profiling shows report endpoints or batch analytics consistently slow
- Cross-user or large history analytics beyond current SQL helpers
- Need for ad-hoc analytical SQL without loading full tables into app memory

**Scope when started:**

- Read-only DuckDB attachment to `backend/data/finguard.db`
- Use for `analyze_spending` / report paths only; **writes stay SQLite**
- Response formatting remains f-string templates (no LLM)
- Document in runbook and [backend-query-audit.md](./backend-query-audit.md)

**References:** [design/chat-backend-target.md](./design/chat-backend-target.md) Layer 4.

---

## Success metrics (before pulling from backlog)

| Item | Gate |
|------|------|
| Semantic Router | ≥95% intent accuracy on `backend/tests/fixtures/utterances.jsonl` + agreed real-user sample |
| Outlines | Rules-only path still default; LLM only when rules return incomplete after one user message |
| Burr | Spike: one flow readable in graph; no regression on golden webhook fixtures |
| DuckDB | Measured slow query or analytics requirement; benchmark before/after |

---
