# VND / profile currency in charts

| Field | Value |
|-------|-------|
| **Spec ID** | DB-07 |
| **Status** | Partial |
| **Phase** | MVP |
| **Priority** | Must |
| **Effort** | S |
| **Catalog refs** | DB-07 |

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

formatMoney uses profile currency not hardcoded USD.

## User stories

- As a user, I want this capability so I can manage personal finances through chat without spreadsheets.

## Current state

Partially implemented: core path exists but gaps limit daily use or Vietnamese coverage.

## Proposal

Fix UI formatter to read profile currency.

## Scope

### In scope

Currency from profile in UI.

### Out of scope

Multi-currency per tx.

## Dependencies

st-02-currency-setting.md

## Acceptance criteria

- [ ] VND displays correctly

## Risks

USD hardcoded today

## Related

[st-02-currency-setting](./st-02-currency-setting.md), [v-06-vnd-default-profile](./v-06-vnd-default-profile.md)

---

## References

- [USE_CASE_CATALOG](../USE_CASE_CATALOG.md)
- [PRODUCT_PLAN](../PRODUCT_PLAN.md)
- [ROADMAP](../ROADMAP.md)
