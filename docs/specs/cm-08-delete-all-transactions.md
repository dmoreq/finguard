# Delete all transactions

| Field | Value |
|-------|-------|
| **Spec ID** | CM-08 |
| **Status** | Shipped |
| **Phase** | MVP |
| **Priority** | Could |
| **Effort** | — |
| **Catalog refs** | CM-08 |

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

Reset all transaction data from header.

## User stories

- As a user, I want this capability so I can manage personal finances through chat without spreadsheets.

## Current state

Shipped in the MVP: behavior is live in backend and/or UI with regression coverage.

## Proposal

Maintain DELETE /data/transactions.

## Scope

### In scope

Clear all txs control.

### Out of scope

Selective delete (see CM-07).

## Dependencies

API route

## Acceptance criteria

- [x] Clear txs works

## Risks

Destructive UX

## Related

[cm-07-delete-single-confirmed](./cm-07-delete-single-confirmed.md)

---

## References

- [USE_CASE_CATALOG](../USE_CASE_CATALOG.md)
- [PRODUCT_PLAN](../PRODUCT_PLAN.md)
- [ROADMAP](../ROADMAP.md)
