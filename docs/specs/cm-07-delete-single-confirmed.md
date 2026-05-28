# Delete single confirmed transaction

| Field | Value |
|-------|-------|
| **Spec ID** | CM-07 |
| **Status** | Future |
| **Phase** | — |
| **Priority** | Should |
| **Effort** | M |
| **Catalog refs** | CM-07 |

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

Remove one historical row without clearing all.

## User stories

- As a user, I want this capability so I can manage personal finances through chat without spreadsheets.

## Current state

Valid user need in the catalog; not scheduled in product or engineering plans yet.

## Proposal

Consider Phase 1 alongside list UI.

## Scope

### In scope

DELETE one transaction.

### Out of scope

Soft-delete only.

## Dependencies

cm-04-transaction-list-ui.md

## Acceptance criteria

TBD

## Risks

Audit trail needs

## Related

[cm-09-soft-delete-audit](./cm-09-soft-delete-audit.md)

---

## References

- [USE_CASE_CATALOG](../USE_CASE_CATALOG.md)
- [PRODUCT_PLAN](../PRODUCT_PLAN.md)
- [ROADMAP](../ROADMAP.md)
