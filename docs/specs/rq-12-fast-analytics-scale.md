# Fast analytics at scale

| Field | Value |
|-------|-------|
| **Spec ID** | RQ-12 |
| **Status** | Roadmap |
| **Phase** | 5 |
| **Priority** | Won't (now) |
| **Effort** | L |
| **Catalog refs** | RQ-12, P4 |

---

## PO decision

| Option | Check |
|--------|-------|
| **Build** | [ ] |
| **Defer** | [ ] |
| **Reject** | [ ] |

**Decision date:** __________
**Notes:**

---

## Problem

Large history aggregations without slow SQLite.

## User stories

- As a user, I want this capability so I can manage personal finances through chat without spreadsheets.

## Current state

Engineering backlog in ROADMAP.md; trigger-driven, not a committed product sprint.

## Proposal

Trigger DuckDB (eng-duckdb-analytics) when profiling shows pain.

## Scope

### In scope

Read-only analytics path.

### Out of scope

DuckDB in unrelated PRs.

## Dependencies

eng-duckdb-analytics.md

## Acceptance criteria

TBD when slow

## Risks

Scope creep

## Related

[eng-duckdb-analytics](./eng-duckdb-analytics.md)

---

## References

- [USE_CASE_CATALOG](../USE_CASE_CATALOG.md)
- [PRODUCT_PLAN](../PRODUCT_PLAN.md)
- [ROADMAP](../ROADMAP.md)
