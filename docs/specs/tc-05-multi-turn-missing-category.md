# Multi-turn — missing category

| Field | Value |
|-------|-------|
| **Spec ID** | TC-05 |
| **Status** | Shipped |
| **Phase** | MVP |
| **Priority** | Should |
| **Effort** | — |
| **Catalog refs** | TC-05 |

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

Bot asks for category when missing.

## User stories

- As a user, I want this capability so I can manage personal finances through chat without spreadsheets.

## Current state

Shipped in the MVP: behavior is live in backend and/or UI with regression coverage.

## Proposal

VI prompts + hints (V-4).

## Scope

### In scope

Collector.

### Out of scope

Default category prefs.

## Dependencies

TC-04

## Acceptance criteria

- [x] Prompt then pending

## Risks

—

## Related

[tc-04-multi-turn-missing-amount](./tc-04-multi-turn-missing-amount.md)

---

## References

- [USE_CASE_CATALOG](../USE_CASE_CATALOG.md)
- [PRODUCT_PLAN](../PRODUCT_PLAN.md)
- [ROADMAP](../ROADMAP.md)
