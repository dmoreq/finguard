# Spending total by period

| Field | Value |
|-------|-------|
| **Spec ID** | RQ-02 |
| **Status** | Shipped |
| **Phase** | MVP |
| **Priority** | Must |
| **Effort** | — |
| **Catalog refs** | RQ-02 |

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

How much did I spend last month.

## User stories

- As a user, I want this capability so I can manage personal finances through chat without spreadsheets.

## Current state

Shipped in the MVP: behavior is live in backend and/or UI with regression coverage.

## Proposal

Maintain analyze_spending intent.

## Scope

### In scope

Period spending total.

### Out of scope

—

## Dependencies

query_spending.py

## Acceptance criteria

- [x] spending report tests

## Risks

EN periods

## Related

[rq-05-period-this-last-month](./rq-05-period-this-last-month.md)

---

## References

- [USE_CASE_CATALOG](../USE_CASE_CATALOG.md)
- [PRODUCT_PLAN](../PRODUCT_PLAN.md)
- [ROADMAP](../ROADMAP.md)
