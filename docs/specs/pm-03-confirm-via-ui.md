# Confirm via UI button

| Field | Value |
|-------|-------|
| **Spec ID** | PM-03 |
| **Status** | Shipped |
| **Phase** | MVP |
| **Priority** | Must |
| **Effort** | — |
| **Catalog refs** | PM-03 |

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

Click Confirm on the pending card to save.

## User stories

- As a user, I want this capability so I can manage personal finances through chat without spreadsheets.

## Current state

Shipped in the MVP: behavior is live in backend and/or UI with regression coverage.

## Proposal

Maintain structured confirm message to webhook.

## Scope

### In scope

Confirm button on TransactionCard.

### Out of scope

—

## Dependencies

TransactionCard, Playwright E2E

## Acceptance criteria

- [x] E2E confirm path

## Risks

—

## Related

[pm-02-confirm-via-chat](./pm-02-confirm-via-chat.md)

---

## References

- [USE_CASE_CATALOG](../USE_CASE_CATALOG.md)
- [PRODUCT_PLAN](../PRODUCT_PLAN.md)
- [ROADMAP](../ROADMAP.md)
