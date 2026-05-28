# Minimal expense (amount + category)

| Field | Value |
|-------|-------|
| **Spec ID** | TC-03 |
| **Status** | Shipped |
| **Phase** | MVP |
| **Priority** | Must |
| **Effort** | — |
| **Catalog refs** | TC-03 |

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

Parse short messages like coffee 4.50 dining.

## User stories

- As a user, I want this capability so I can manage personal finances through chat without spreadsheets.

## Current state

Shipped in the MVP: behavior is live in backend and/or UI with regression coverage.

## Proposal

Enhance VND (V-3).

## Scope

### In scope

Rule extraction.

### Out of scope

LLM-only.

## Dependencies

RulesFieldExtractor

## Acceptance criteria

- [x] English minimal parse
- [ ] 50k ăn trưa

## Risks

Ambiguous categories

## Related

[v-03-vnd-amount-parsing](./v-03-vnd-amount-parsing.md)

---

## References

- [USE_CASE_CATALOG](../USE_CASE_CATALOG.md)
- [PRODUCT_PLAN](../PRODUCT_PLAN.md)
- [ROADMAP](../ROADMAP.md)
