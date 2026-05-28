# Soft-delete / audit trail

| Field | Value |
|-------|-------|
| **Spec ID** | CM-09 |
| **Status** | Partial |
| **Phase** | MVP |
| **Priority** | Could |
| **Effort** | S |
| **Catalog refs** | CM-09 |

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

Discarded and deleted rows tracked but hidden from default API.

## User stories

- As a user, I want this capability so I can manage personal finances through chat without spreadsheets.

## Current state

Partially implemented: core path exists but gaps limit daily use or Vietnamese coverage.

## Proposal

discarded status exists; expose audit API later if needed.

## Scope

### In scope

DB status for discarded.

### Out of scope

Full audit UI.

## Dependencies

SQLite schema

## Acceptance criteria

- [x] discarded in DB

## Risks

Hidden from list API

## Related

[cm-07-delete-single-confirmed](./cm-07-delete-single-confirmed.md)

---

## References

- [USE_CASE_CATALOG](../USE_CASE_CATALOG.md)
- [PRODUCT_PLAN](../PRODUCT_PLAN.md)
- [ROADMAP](../ROADMAP.md)
