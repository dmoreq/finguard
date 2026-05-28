# Confirm pending via chat

| Field | Value |
|-------|-------|
| **Spec ID** | PM-02 |
| **Status** | Shipped |
| **Phase** | MVP |
| **Priority** | Must |
| **Effort** | — |
| **Catalog refs** | PM-02 |

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

Say confirm or yes to save the pending transaction.

## User stories

- As a user, I want this capability so I can manage personal finances through chat without spreadsheets.

## Current state

Shipped in the MVP: behavior is live in backend and/or UI with regression coverage.

## Proposal

Maintain manage_confirm; add Vietnamese phrases in Phase 0.5.

## Scope

### In scope

English confirm keywords and webhook handler.

### Out of scope

Saving without explicit confirm.

## Dependencies

DialogueEngine

## Acceptance criteria

- [x] Confirmed row persisted

## Risks

Vietnamese blocked until 0.5

## Related

[pm-10-vietnamese-pending-actions](./pm-10-vietnamese-pending-actions.md), [v-02-vietnamese-pending-replies](./v-02-vietnamese-pending-replies.md)

---

## References

- [USE_CASE_CATALOG](../USE_CASE_CATALOG.md)
- [PRODUCT_PLAN](../PRODUCT_PLAN.md)
- [ROADMAP](../ROADMAP.md)
