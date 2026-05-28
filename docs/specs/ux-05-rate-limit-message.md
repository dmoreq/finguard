# Rate limit friendly message

| Field | Value |
|-------|-------|
| **Spec ID** | UX-05 |
| **Status** | Shipped |
| **Phase** | MVP |
| **Priority** | Should |
| **Effort** | — |
| **Catalog refs** | UX-05 |

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

429 returns user-friendly message.

## User stories

- As a user, I want this capability so I can manage personal finances through chat without spreadsheets.

## Current state

Shipped in the MVP: behavior is live in backend and/or UI with regression coverage.

## Proposal

Maintain /api/chat rate limit response.

## Scope

### In scope

429 handling.

### Out of scope

Distributed limit (AU-08).

## Dependencies

middleware

## Acceptance criteria

- [x] 429 returned

## Risks

Single-node limit

## Related

[au-08-distributed-rate-limiting](./au-08-distributed-rate-limiting.md)

---

## References

- [USE_CASE_CATALOG](../USE_CASE_CATALOG.md)
- [PRODUCT_PLAN](../PRODUCT_PLAN.md)
- [ROADMAP](../ROADMAP.md)
