# List confirmed transactions (chat)

| Field | Value |
|-------|-------|
| **Spec ID** | CM-01 |
| **Status** | Shipped |
| **Phase** | MVP |
| **Priority** | Should |
| **Effort** | — |
| **Catalog refs** | CM-01 |

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

Ask to show recent transactions in chat.

## User stories

- As a user, I want this capability so I can manage personal finances through chat without spreadsheets.

## Current state

Shipped in the MVP: behavior is live in backend and/or UI with regression coverage.

## Proposal

Maintain list_transactions intent; add VI routing.

## Scope

### In scope

Chat list of confirmed rows.

### Out of scope

Rich filters in chat.

## Dependencies

DialogueEngine

## Acceptance criteria

- [x] list_transactions works EN

## Risks

VI Phase 0.5

## Related

[cm-02-list-period-filter-chat](./cm-02-list-period-filter-chat.md)

---

## References

- [USE_CASE_CATALOG](../USE_CASE_CATALOG.md)
- [PRODUCT_PLAN](../PRODUCT_PLAN.md)
- [ROADMAP](../ROADMAP.md)
