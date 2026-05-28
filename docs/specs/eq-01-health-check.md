# Chat backend health check

| Field | Value |
|-------|-------|
| **Spec ID** | EQ-01 |
| **Status** | Shipped |
| **Phase** | MVP |
| **Priority** | Must |
| **Effort** | — |
| **Catalog refs** | EQ-01 |

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

App detects backend outage via /health.

## User stories

- As a user, I want this capability so I can manage personal finances through chat without spreadsheets.

## Current state

Shipped in the MVP: behavior is live in backend and/or UI with regression coverage.

## Proposal

Maintain health endpoint + smoke scripts.

## Scope

### In scope

/health returns OK.

### Out of scope

—

## Dependencies

health route

## Acceptance criteria

- [x] /health

## Risks

—

## Related

[ux-04-error-retry](./ux-04-error-retry.md)

---

## References

- [USE_CASE_CATALOG](../USE_CASE_CATALOG.md)
- [PRODUCT_PLAN](../PRODUCT_PLAN.md)
- [ROADMAP](../ROADMAP.md)
