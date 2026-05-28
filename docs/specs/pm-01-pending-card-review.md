# Review pending card in chat

| Field | Value |
|-------|-------|
| **Spec ID** | PM-01 |
| **Status** | Shipped |
| **Phase** | MVP |
| **Priority** | Must |
| **Effort** | — |
| **Catalog refs** | PM-01 |

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

See amount, category, and date on the pending card before save.

## User stories

- As a user, I want this capability so I can manage personal finances through chat without spreadsheets.

## Current state

Shipped in the MVP: behavior is live in backend and/or UI with regression coverage.

## Proposal

Maintain transaction_pending payload and TransactionCard rendering.

## Scope

### In scope

Pending card in chat with all fields.

### Out of scope

Auto-confirm without review.

## Dependencies

chat-payloads.json, TransactionCard

## Acceptance criteria

- [x] Card shows pending fields

## Risks

Low

## Related

[pm-10-vietnamese-pending-actions](./pm-10-vietnamese-pending-actions.md)

---

## References

- [USE_CASE_CATALOG](../USE_CASE_CATALOG.md)
- [PRODUCT_PLAN](../PRODUCT_PLAN.md)
- [ROADMAP](../ROADMAP.md)
