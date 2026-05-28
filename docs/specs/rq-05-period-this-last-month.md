# Period: this month / last month

| Field | Value |
|-------|-------|
| **Spec ID** | RQ-05 |
| **Status** | Shipped |
| **Phase** | MVP |
| **Priority** | Must |
| **Effort** | — |
| **Catalog refs** | RQ-05 |

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

Default reporting windows for this/last month.

## User stories

- As a user, I want this capability so I can manage personal finances through chat without spreadsheets.

## Current state

Shipped in the MVP: behavior is live in backend and/or UI with regression coverage.

## Proposal

Maintain parse_period_from_text.

## Scope

### In scope

this month, last month.

### Out of scope

Custom ranges.

## Dependencies

utils/dates

## Acceptance criteria

- [x] EN month windows

## Risks

TZ edge cases

## Related

[st-03-timezone-setting](./st-03-timezone-setting.md)

---

## References

- [USE_CASE_CATALOG](../USE_CASE_CATALOG.md)
- [PRODUCT_PLAN](../PRODUCT_PLAN.md)
- [ROADMAP](../ROADMAP.md)
