# Chat backend — target architecture

**Status:** Target (not fully implemented)
**Last updated:** 2026-05-28
**Backlog:** [ROADMAP.md](../ROADMAP.md)

## Summary

Four decoupled layers: **route** → **dialogue state** → **extract (LLM only when needed)** → **persist and report**. Goals: deterministic money flows, minimal tokens, no Rasa Pro.

**As-built stack and layer mapping:** [ARCHITECTURE.md](../ARCHITECTURE.md). **Burr** and **DuckDB** are on the [backlog](../ROADMAP.md), not required for the current release.

---

## Layer 1: Routing (zero-token intent)

**Tool (target):** semantic-router with a lightweight encoder (e.g. `all-MiniLM-L6-v2`).

**Mechanism:** Static routes with sample utterances; cosine similarity → `route_id`. No LLM.

**Examples:**

- `log_expense`: "spent 50k on food", "bought coffee"
- `check_balance`, `analyze_spending`, `manage_pending`, …

**Guards (required in implementation):**

- While `confirmation_pending`, short replies (`yes`, `no`, `discard`, amount/category edits) must route to `manage_pending`, not chitchat or generic intents.
- Low confidence → `unknown` + clarifying template (still no LLM).

**Cost:** 0 tokens.

---

## Layer 2: State management (deterministic dialogue)

**Tool (target):** Burr graph — explicit nodes and transitions.

**Mechanism:** `route_id` starts a graph execution. State holds `partial_transaction`, `dialogue_phase`, `last_transaction_id`, `confirmation_pending`, etc.

**Core FSM (product requirement, any implementation):**

```text
idle → collecting → awaiting_confirmation → (confirm | discard | edit) → idle
```

**Nodes (conceptual):**

- Ask user for missing slots (static prompts)
- Call extraction when text may complete slots
- Call services to create pending row, confirm, discard, update
- Analytics paths skip extraction when intent is report-only

**Why not LangGraph / agents:** Avoid open-ended reasoning loops on financial actions.

**Shipped alternative:** `backend/actions/chat/engine.py` — same responsibilities until [Burr is adopted](../ROADMAP.md#burr-backlog-detail).

**Cost:** 0 tokens.

---

## Layer 3: Entity extraction (schema-bound, optional LLM)

**Tool (target):** Outlines + Gemini Flash API (or local model via vLLM later).

**Policy:** Rules first; invoke Outlines only when rules cannot fill required slots.

**Schema (illustrative):**

```python
class ExpenseSchema(BaseModel):
    amount: float = Field(..., gt=0)
    category: str = Field(...)
    description: str | None = None  # optional — do not force the model to invent text
```

**Error handling (must map to FSM transitions):**

| Status | Action |
|--------|--------|
| `success` | Merge into `partial_transaction`; maybe confirm or ask next slot |
| `validation_error` | Re-ask for amount/category; never write DB |
| `api_error` | User-facing fallback; optional rule retry; never write DB |

**Configuration:** `GEMINI_API_KEY` from environment only — never commit keys in docs or code.

**ADR note:** [ADR-003](../decisions/003-low-cost-chat-backend.md) mentioned Instructor; [ADR-004](../decisions/004-chat-backend-evolution.md) records Outlines as the preferred structured-extraction library when LLM extract ships.

**Cost:** Low — bounded calls per extract step, not per turn for routing or reports.

---

## Layer 4: Execution and analytics

**Writes:** Validated transactions → SQLite (`confirmed` only after user confirms pending card).

**Reads (target):** For heavy aggregates, DuckDB queries the SQLite file; format results with f-string templates (no LLM).

**Reads (shipped):** Service-layer SQL in Python — sufficient for personal scale.

**DuckDB:** [Backlog](../ROADMAP.md#duckdb-backlog-detail) — adopt when analytics performance requires it.

**Cost:** 0 tokens for report wording.

---

## Flows the design must cover

These are implemented today and must remain in any target stack:

| Flow | Layers used |
|------|-------------|
| Record expense/income | 1 → 2 → (3 if needed) → 4 |
| Pending confirm / discard / edit | 1 → 2 → 4 |
| Balance / spending report | 1 → 2 → 4 (period parsing: **rules**, not LLM) |
| No pending when user says "confirm" | 2 guard + template |

**UI contract:** [chat-payloads.json](../schemas/chat-payloads.json) (`transaction_pending`, `balance`, `spending_report`, …).

**Profile:** Currency and timezone from SQLite profile affect formatting and period boundaries.

---

## System diagram (target)

```text
User message
     │
     ▼
┌─────────────┐
│ Layer 1     │  semantic-router (local embeddings)
│ Routing     │
└──────┬──────┘
       │ route_id
       ▼
┌─────────────┐
│ Layer 2     │  Burr FSM (backlog) / engine.py (today)
│ State       │
└──────┬──────┘
       │ needs slots?
       ▼
┌─────────────┐     rules OK ──────────────┐
│ Layer 3     │                            │
│ Outlines    │  (optional fallback)       │
└──────┬──────┘                            │
       │ structured payload                │
       ▼                                    ▼
┌─────────────┐                      ┌─────────────┐
│ Layer 4     │  SQLite writes       │ Layer 4     │  SQL / DuckDB reads
│ OLTP        │                      │ OLAP        │  (DuckDB: backlog)
└─────────────┘                      └─────────────┘
       │                                    │
       └──────────────┬─────────────────────┘
                      ▼
              Webhook JSON → Next.js
```

---

## Non-goals

- Agent with tools for every turn
- LLM-generated balance or spending narratives
- DuckDB before measured need
- Replacing working rule extraction with LLM for simple utterances
