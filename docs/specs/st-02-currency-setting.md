# Set currency

| Field | Value |
|-------|-------|
| **Spec ID** | ST-02 |
| **Status** | Shipped |
| **Phase** | MVP |
| **Priority** | Must |
| **Effort** | — |
| **Catalog refs** | ST-02 |

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

Choose VND, USD, etc.

## User stories

- As a user, I want this capability so I can manage personal finances through chat without spreadsheets.

## Current state

Shipped in the MVP: behavior is live in backend and/or UI with regression coverage.

## Proposal

Maintain currency list; default VND in 0.5 (V-6).

## Scope

### In scope

Profile currency.

### Out of scope

Per-tx currency.

## Dependencies

schema profile

## Acceptance criteria

- [x] VND in list

## Risks

Default still USD

## Related

[v-06-vnd-default-profile](./v-06-vnd-default-profile.md), [db-07-profile-currency-charts](./db-07-profile-currency-charts.md)

---

## References

- [USE_CASE_CATALOG](../USE_CASE_CATALOG.md)
- [PRODUCT_PLAN](../PRODUCT_PLAN.md)
- [ROADMAP](../ROADMAP.md)
