# Period: 7d / 30d / 3m / YTD

| Field | Value |
|-------|-------|
| **Spec ID** | RQ-06 |
| **Status** | Partial |
| **Phase** | MVP |
| **Priority** | Should |
| **Effort** | S |
| **Catalog refs** | RQ-06 |

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

Extended windows like last 7 days and YTD.

## User stories

- As a user, I want this capability so I can manage personal finances through chat without spreadsheets.

## Current state

Partially implemented: core path exists but gaps limit daily use or Vietnamese coverage.

## Proposal

English regex only; add VI.

## Scope

### In scope

Extended period tokens EN.

### Out of scope

Arbitrary ranges.

## Dependencies

parse_period_from_text

## Acceptance criteria

- [x] EN 7d/30d partial

## Risks

VI missing

## Related

[rq-07-vietnamese-report-questions](./rq-07-vietnamese-report-questions.md)

---

## References

- [USE_CASE_CATALOG](../USE_CASE_CATALOG.md)
- [PRODUCT_PLAN](../PRODUCT_PLAN.md)
- [ROADMAP](../ROADMAP.md)
