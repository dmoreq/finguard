# List with period filter (chat)

| Field | Value |
|-------|-------|
| **Spec ID** | CM-02 |
| **Status** | Partial |
| **Phase** | MVP |
| **Priority** | Should |
| **Effort** | S |
| **Catalog refs** | CM-02 |

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

Filter list by last 7 days, this month, etc.

## User stories

- As a user, I want this capability so I can manage personal finances through chat without spreadsheets.

## Current state

Partially implemented: core path exists but gaps limit daily use or Vietnamese coverage.

## Proposal

Extend period parsing for Vietnamese.

## Scope

### In scope

English period patterns.

### Out of scope

Custom date ranges.

## Dependencies

parse_period_from_text

## Acceptance criteria

- [x] EN periods

## Risks

VI periods missing

## Related

[rq-07-vietnamese-report-questions](./rq-07-vietnamese-report-questions.md)

---

## References

- [USE_CASE_CATALOG](../USE_CASE_CATALOG.md)
- [PRODUCT_PLAN](../PRODUCT_PLAN.md)
- [ROADMAP](../ROADMAP.md)
