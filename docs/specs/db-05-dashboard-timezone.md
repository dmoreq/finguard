# Dashboard respects timezone

| Field | Value |
|-------|-------|
| **Spec ID** | DB-05 |
| **Status** | Partial |
| **Phase** | MVP |
| **Priority** | Should |
| **Effort** | S |
| **Catalog refs** | DB-05 |

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

Month boundaries match user timezone.

## User stories

- As a user, I want this capability so I can manage personal finances through chat without spreadsheets.

## Current state

Partially implemented: core path exists but gaps limit daily use or Vietnamese coverage.

## Proposal

Align client month with profile timezone (ST-03).

## Scope

### In scope

Backend TZ used; client month may drift.

### Out of scope

—

## Dependencies

st-03-timezone-setting.md

## Acceptance criteria

- [ ] Month boundary test TZ

## Risks

Client vs server month

## Related

[st-03-timezone-setting](./st-03-timezone-setting.md)

---

## References

- [USE_CASE_CATALOG](../USE_CASE_CATALOG.md)
- [PRODUCT_PLAN](../PRODUCT_PLAN.md)
- [ROADMAP](../ROADMAP.md)
