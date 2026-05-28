# Discard via UI button

| Field | Value |
|-------|-------|
| **Spec ID** | PM-05 |
| **Status** | Shipped |
| **Phase** | MVP |
| **Priority** | Must |
| **Effort** | — |
| **Catalog refs** | PM-05 |

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

Click Discard on the card to cancel pending.

## User stories

- As a user, I want this capability so I can manage personal finances through chat without spreadsheets.

## Current state

Shipped in the MVP: behavior is live in backend and/or UI with regression coverage.

## Proposal

Keep E2E discard-transaction.spec.ts green.

## Scope

### In scope

UI sends discard to backend.

### Out of scope

—

## Dependencies

TransactionCard

## Acceptance criteria

- [x] E2E discard

## Risks

—

## Related

[pm-04-discard-via-chat](./pm-04-discard-via-chat.md)

---

## References

- [USE_CASE_CATALOG](../USE_CASE_CATALOG.md)
- [PRODUCT_PLAN](../PRODUCT_PLAN.md)
- [ROADMAP](../ROADMAP.md)
