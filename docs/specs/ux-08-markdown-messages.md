# Markdown in messages

| Field | Value |
|-------|-------|
| **Spec ID** | UX-08 |
| **Status** | Shipped |
| **Phase** | MVP |
| **Priority** | Could |
| **Effort** | — |
| **Catalog refs** | UX-08 |

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

Bold and lists in bot replies.

## User stories

- As a user, I want this capability so I can manage personal finances through chat without spreadsheets.

## Current state

Shipped in the MVP: behavior is live in backend and/or UI with regression coverage.

## Proposal

Maintain markdown.tsx rendering.

## Scope

### In scope

Markdown subset in chat.

### Out of scope

Unsafe HTML.

## Dependencies

markdown.tsx

## Acceptance criteria

- [x] Renders markdown

## Risks

—

## Related

[ux-09-safe-markdown](./ux-09-safe-markdown.md)

---

## References

- [USE_CASE_CATALOG](../USE_CASE_CATALOG.md)
- [PRODUCT_PLAN](../PRODUCT_PLAN.md)
- [ROADMAP](../ROADMAP.md)
