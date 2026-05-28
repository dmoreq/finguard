# Persist transactions locally

| Field | Value |
|-------|-------|
| **Spec ID** | DS-01 |
| **Status** | Shipped |
| **Phase** | MVP |
| **Priority** | Must |
| **Effort** | — |
| **Catalog refs** | DS-01 |

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

SQLite finguard.db on disk.

## User stories

- As a user, I want this capability so I can manage personal finances through chat without spreadsheets.

## Current state

Shipped in the MVP: behavior is live in backend and/or UI with regression coverage.

## Proposal

Maintain SQLite OLTP.

## Scope

### In scope

Local SQLite file.

### Out of scope

Postgres (Phase 4).

## Dependencies

backend/data

## Acceptance criteria

- [x] DB file exists

## Risks

Single-user

## Related

[au-04-postgres-migration](./au-04-postgres-migration.md)

---

## References

- [USE_CASE_CATALOG](../USE_CASE_CATALOG.md)
- [PRODUCT_PLAN](../PRODUCT_PLAN.md)
- [ROADMAP](../ROADMAP.md)
