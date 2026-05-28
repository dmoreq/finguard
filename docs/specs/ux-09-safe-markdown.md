# Safe markdown (no XSS)

| Field | Value |
|-------|-------|
| **Spec ID** | UX-09 |
| **Status** | Shipped |
| **Phase** | MVP |
| **Priority** | Must |
| **Effort** | — |
| **Catalog refs** | UX-09 |

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

HTML escaped in rendered messages.

## User stories

- As a user, I want this capability so I can manage personal finances through chat without spreadsheets.

## Current state

Shipped in the MVP: behavior is live in backend and/or UI with regression coverage.

## Proposal

Maintain escape rules; a11y tests.

## Scope

### In scope

XSS-safe rendering.

### Out of scope

Raw HTML from user.

## Dependencies

markdown.tsx

## Acceptance criteria

- [x] a11y-smoke

## Risks

—

## Related

[ux-08-markdown-messages](./ux-08-markdown-messages.md)

---

## References

- [USE_CASE_CATALOG](../USE_CASE_CATALOG.md)
- [PRODUCT_PLAN](../PRODUCT_PLAN.md)
- [ROADMAP](../ROADMAP.md)
