# Idempotent confirm

| Field | Value |
|-------|-------|
| **Spec ID** | PM-13 |
| **Status** | Shipped |
| **Phase** | MVP |
| **Priority** | Must |
| **Effort** | — |
| **Catalog refs** | PM-13 |

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

Confirming twice must not create duplicate transactions.

## User stories

- As a user, I want this capability so I can manage personal finances through chat without spreadsheets.

## Current state

Shipped in the MVP: behavior is live in backend and/or UI with regression coverage.

## Proposal

Keep confirmed guard in update_transaction.

## Scope

### In scope

Idempotent confirm handler.

### Out of scope

—

## Dependencies

services/transactions

## Acceptance criteria

- [x] Second confirm is no-op

## Risks

—

## Related

[pm-02-confirm-via-chat](./pm-02-confirm-via-chat.md)

---

## References

- [USE_CASE_CATALOG](../USE_CASE_CATALOG.md)
- [PRODUCT_PLAN](../PRODUCT_PLAN.md)
- [ROADMAP](../ROADMAP.md)
