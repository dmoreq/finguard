# DuckDB analytics on SQLite file

| Field | Value |
|-------|-------|
| **Spec ID** | ENG-DUCK |
| **Status** | Roadmap |
| **Phase** | 5 |
| **Priority** | Won't (now) |
| **Effort** | L |
| **Catalog refs** | ROADMAP P4 |

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

Read-only columnar aggregations on finguard.db.

## User stories

- As a user, I want this capability so I can manage personal finances through chat without spreadsheets.

## Current state

Engineering backlog in ROADMAP.md; trigger-driven, not a committed product sprint.

## Proposal

When report endpoints slow.

## Scope

### In scope

DuckDB read path.

### Out of scope

DuckDB writes

## Dependencies

DuckDB

## Acceptance criteria

TBD

## Risks

Ops

## Related

[eq-07-duckdb-fast-reports](./eq-07-duckdb-fast-reports.md), [rq-12-fast-analytics-scale](./rq-12-fast-analytics-scale.md)

---

## References

- [USE_CASE_CATALOG](../USE_CASE_CATALOG.md)
- [PRODUCT_PLAN](../PRODUCT_PLAN.md)
- [ROADMAP](../ROADMAP.md)
