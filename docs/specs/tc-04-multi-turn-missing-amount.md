# Multi-turn — missing amount

| Field | Value |
|-------|-------|
| **Spec ID** | TC-04 |
| **Status** | Shipped |
| **Phase** | MVP |
| **Priority** | Should |
| **Effort** | — |
| **Catalog refs** | TC-04 |

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

Bot asks for amount when missing.

## User stories

- As a user, I want this capability so I can manage personal finances through chat without spreadsheets.

## Current state

Shipped in the MVP: behavior is live in backend and/or UI with regression coverage.

## Proposal

VI prompts (V-8).

## Scope

### In scope

collecting phase.

### Out of scope

Infinite loops.

## Dependencies

chat_sessions

## Acceptance criteria

- [x] Second turn completes

## Risks

—

## Related

[v-08-vietnamese-bot-templates](./v-08-vietnamese-bot-templates.md)

---

## References

- [USE_CASE_CATALOG](../USE_CASE_CATALOG.md)
- [PRODUCT_PLAN](../PRODUCT_PLAN.md)
- [ROADMAP](../ROADMAP.md)
