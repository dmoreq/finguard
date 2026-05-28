# Set timezone

| Field | Value |
|-------|-------|
| **Spec ID** | ST-03 |
| **Status** | Shipped |
| **Phase** | MVP |
| **Priority** | Must |
| **Effort** | — |
| **Catalog refs** | ST-03 |

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

Asia/Ho_Chi_Minh and other TZs.

## User stories

- As a user, I want this capability so I can manage personal finances through chat without spreadsheets.

## Current state

Shipped in the MVP: behavior is live in backend and/or UI with regression coverage.

## Proposal

Maintain timezone on profile for reports.

## Scope

### In scope

Timezone field.

### Out of scope

—

## Dependencies

PATCH profile

## Acceptance criteria

- [x] E2E timezone

## Risks

Dashboard client TZ

## Related

[db-05-dashboard-timezone](./db-05-dashboard-timezone.md)

---

## References

- [USE_CASE_CATALOG](../USE_CASE_CATALOG.md)
- [PRODUCT_PLAN](../PRODUCT_PLAN.md)
- [ROADMAP](../ROADMAP.md)
