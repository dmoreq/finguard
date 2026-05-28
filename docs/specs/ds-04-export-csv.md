# Export transactions CSV

| Field | Value |
|-------|-------|
| **Spec ID** | DS-04 |
| **Status** | Shipped |
| **Phase** | MVP |
| **Priority** | Should |
| **Effort** | — |
| **Catalog refs** | DS-04 |

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

Download CSV for Excel.

## User stories

- As a user, I want this capability so I can manage personal finances through chat without spreadsheets.

## Current state

Shipped in the MVP: behavior is live in backend and/or UI with regression coverage.

## Proposal

Maintain /api/transactions/export E2E.

## Scope

### In scope

CSV export endpoint.

### Out of scope

Encrypted export.

## Dependencies

export route

## Acceptance criteria

- [x] E2E export

## Risks

—

## Related

[ds-06-backup-restore](./ds-06-backup-restore.md)

---

## References

- [USE_CASE_CATALOG](../USE_CASE_CATALOG.md)
- [PRODUCT_PLAN](../PRODUCT_PLAN.md)
- [ROADMAP](../ROADMAP.md)
