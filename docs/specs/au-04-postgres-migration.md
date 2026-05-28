# Postgres instead of SQLite

| Field | Value |
|-------|-------|
| **Spec ID** | AU-04 |
| **Status** | Planned |
| **Phase** | 4 |
| **Priority** | Must (hosted) |
| **Effort** | XL |
| **Catalog refs** | AU-04, U-2 |

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

Multi-user OLTP on Postgres.

## User stories

- As a user, I want this capability so I can manage personal finances through chat without spreadsheets.

## Current state

Planned in PRODUCT_PLAN with a phase ID; design agreed, implementation not complete.

## Proposal

Migrate schema + queries from SQLite.

## Scope

### In scope

Postgres primary DB.

### Out of scope

SQLite hosted prod

## Dependencies

Phase 4

## Acceptance criteria

TBD

## Risks

Data migration

## Related

[ds-07-cloud-sync](./ds-07-cloud-sync.md)

---

## References

- [USE_CASE_CATALOG](../USE_CASE_CATALOG.md)
- [PRODUCT_PLAN](../PRODUCT_PLAN.md)
- [ROADMAP](../ROADMAP.md)
