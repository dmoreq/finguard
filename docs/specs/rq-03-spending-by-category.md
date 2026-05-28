# Spending by category

| Field | Value |
|-------|-------|
| **Spec ID** | RQ-03 |
| **Status** | Shipped |
| **Phase** | MVP |
| **Priority** | Must |
| **Effort** | — |
| **Catalog refs** | RQ-03 |

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

Category breakdown in spending report card.

## User stories

- As a user, I want this capability so I can manage personal finances through chat without spreadsheets.

## Current state

Shipped in the MVP: behavior is live in backend and/or UI with regression coverage.

## Proposal

Maintain spending_report payload.

## Scope

### In scope

Category breakdown in template.

### Out of scope

LLM narrative.

## Dependencies

SQL templates

## Acceptance criteria

- [x] category rows in report

## Risks

VI labels later

## Related

[db-08-vietnamese-category-labels](./db-08-vietnamese-category-labels.md)

---

## References

- [USE_CASE_CATALOG](../USE_CASE_CATALOG.md)
- [PRODUCT_PLAN](../PRODUCT_PLAN.md)
- [ROADMAP](../ROADMAP.md)
