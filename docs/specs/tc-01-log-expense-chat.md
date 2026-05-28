# Log expense via chat (one message)

| Field | Value |
|-------|-------|
| **Spec ID** | TC-01 |
| **Status** | Shipped |
| **Phase** | MVP |
| **Priority** | Must |
| **Effort** | — |
| **Catalog refs** | TC-01 |

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

Record spending in natural language with confirm-before-save.

## User stories

- As a user, I want this capability so I can manage personal finances through chat without spreadsheets.

## Current state

Shipped in the MVP: behavior is live in backend and/or UI with regression coverage.

## Proposal

Maintain; extend Vietnamese (Phase 0.5) and optional payment account (AC-01).

## Scope

### In scope

Single-turn expense → pending card.

### Out of scope

Auto-confirm.

## Dependencies

DialogueEngine, record_transaction.

## Acceptance criteria

- [x] English expense → pending
- [ ] VI golden flow step 1

## Risks

VI blocked until 0.5

## Related

[tc-09-vietnamese-expense-chat](./tc-09-vietnamese-expense-chat.md), [v-03-vnd-amount-parsing](./v-03-vnd-amount-parsing.md)

---

## References

- [USE_CASE_CATALOG](../USE_CASE_CATALOG.md)
- [PRODUCT_PLAN](../PRODUCT_PLAN.md)
- [ROADMAP](../ROADMAP.md)
