# Balance / net (income − expenses)

| Field | Value |
|-------|-------|
| **Spec ID** | RQ-01 |
| **Status** | Shipped |
| **Phase** | MVP |
| **Priority** | Must |
| **Effort** | — |
| **Catalog refs** | RQ-01 |

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

What's my balance this month via chat.

## User stories

- As a user, I want this capability so I can manage personal finances through chat without spreadsheets.

## Current state

Shipped in the MVP: behavior is live in backend and/or UI with regression coverage.

## Proposal

Maintain check_balance and balance payload.

## Scope

### In scope

Template SQL balance report.

### Out of scope

LLM prose reports.

## Dependencies

get_balance.py

## Acceptance criteria

- [x] test_webhook_reports balance

## Risks

VI Phase 0.5

## Related

[rq-07-vietnamese-report-questions](./rq-07-vietnamese-report-questions.md)

---

## References

- [USE_CASE_CATALOG](../USE_CASE_CATALOG.md)
- [PRODUCT_PLAN](../PRODUCT_PLAN.md)
- [ROADMAP](../ROADMAP.md)
