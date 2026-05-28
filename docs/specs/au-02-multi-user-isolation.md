# Multi-user data isolation

| Field | Value |
|-------|-------|
| **Spec ID** | AU-02 |
| **Status** | Future |
| **Phase** | 4 |
| **Priority** | Must (hosted) |
| **Effort** | XL |
| **Catalog refs** | AU-02, U-3 |

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

Each user sees only own data.

## User stories

- As a user, I want this capability so I can manage personal finances through chat without spreadsheets.

## Current state

Valid user need in the catalog; not scheduled in product or engineering plans yet.

## Proposal

RLS + user_id on all queries.

## Scope

### In scope

Per-user data partition.

### Out of scope

Shared local user

## Dependencies

Postgres

## Acceptance criteria

TBD

## Risks

Migration

## Related

[au-04-postgres-migration](./au-04-postgres-migration.md)

---

## References

- [USE_CASE_CATALOG](../USE_CASE_CATALOG.md)
- [PRODUCT_PLAN](../PRODUCT_PLAN.md)
- [ROADMAP](../ROADMAP.md)
