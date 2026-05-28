# ADR-004: Chat backend evolution (shipped stack vs target)

## Status

Accepted

## Date

2026-05-28

## Context

[ADR-003](./003-low-cost-chat-backend.md) named Semantic Router, Burr, Instructor, and SQLite. The shipped stack ([ARCHITECTURE.md](../ARCHITECTURE.md)) uses keyword routing, `engine.py`, rule extraction, and SQLite only. [design/chat-backend-target.md](../design/chat-backend-target.md) and [ROADMAP.md](../ROADMAP.md) define incremental upgrades (Outlines instead of Instructor; Burr and DuckDB on the backlog).

## Decision

1. **ADR-003 remains accepted** for the architectural direction (no Rasa; deterministic dialogue; LLM only for extraction; SQLite truth).
2. **The shipped stack is the valid v1** until roadmap triggers are met.
3. **Evolution order** (see [ROADMAP.md](../ROADMAP.md)):
   - P1: Semantic Router (+ confirmation_pending overrides)
   - P2: Outlines + Gemini as rules-first fallback
   - P3: **Burr** — backlog until FSM complexity warrants it
   - P4: **DuckDB** — backlog until analytics performance warrants it
4. **When LLM extraction is added**, use **Outlines + Pydantic**, not Instructor, unless a future ADR supersedes this.
5. **Burr and DuckDB are not blockers** for feature work on the current `engine.py` + SQLite path.

## Alternatives considered

| Alternative | Rejected because |
|-------------|------------------|
| Revert to ADR-003 tool names immediately | Working tests and simpler ops; no user-facing gap |
| Adopt Burr + DuckDB in one migration | Large diff; Burr/DuckDB add little until scale/complexity grows |
| Keep Instructor per ADR-003 | Outlines chosen for constrained JSON generation in target doc; either is acceptable; pick one — Outlines documented in target design |

## Consequences

- **Positive:** Clear “as-built” vs “target” docs; backlog visible for Burr and DuckDB.
- **Positive:** Contributors can ship on `engine.py` without waiting for Burr.
- **Negative:** ADR-003 text is partially stale on tool names — this ADR and [ROADMAP.md](../ROADMAP.md) are the source of truth for evolution.
- **Action:** Update onboarding links to [design/chat-backend-target.md](../design/chat-backend-target.md) and [ROADMAP.md](../ROADMAP.md).

## Verification

Golden webhook fixtures pass on the shipped stack until a roadmap item explicitly changes behavior.
