# Edit amount via chat

| Field | Value |
|-------|-------|
| **Spec ID** | PM-06 |
| **Status** | Shipped |
| **Phase** | MVP |
| **Priority** | Must |
| **Effort** | — |
| **Catalog refs** | PM-06 |

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

Change pending amount before confirm, e.g. change amount to 50.

## User stories

- As a user, I want this capability so I can manage personal finances through chat without spreadsheets.

## Current state

Shipped in the MVP: behavior is live in backend and/or UI with regression coverage.

## Proposal

Maintain edit rules; add Vietnamese (V-5).

## Scope

### In scope

Amount edit on pending only.

### Out of scope

Post-confirm amount edit.

## Dependencies

Pending handler

## Acceptance criteria

- [x] Webhook edit tests

## Risks

VI edit phrases

## Related

[v-05-vietnamese-edit-phrases](./v-05-vietnamese-edit-phrases.md)

---

## References

- [USE_CASE_CATALOG](../USE_CASE_CATALOG.md)
- [PRODUCT_PLAN](../PRODUCT_PLAN.md)
- [ROADMAP](../ROADMAP.md)
