# LLM extract fallback

| Field | Value |
|-------|-------|
| **Spec ID** | TC-08 |
| **Status** | Partial |
| **Phase** | P2 |
| **Priority** | Should |
| **Effort** | S |
| **Catalog refs** | TC-08 |

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

Parse when rules fail.

## User stories

- As a user, I want this capability so I can manage personal finances through chat without spreadsheets.

## Current state

Partially implemented: core path exists but gaps limit daily use or Vietnamese coverage.

## Proposal

Enable for VI beta; log usage.

## Scope

### In scope

Rules-first LLM gap-fill.

### Out of scope

LLM every turn.

## Dependencies

GEMINI_API_KEY

## Acceptance criteria

- [x] No DB on error
- [ ] VI with LLM on

## Risks

SDK deprecation

## Related

[eng-outlines-structured-extract](./eng-outlines-structured-extract.md)

---

## References

- [USE_CASE_CATALOG](../USE_CASE_CATALOG.md)
- [PRODUCT_PLAN](../PRODUCT_PLAN.md)
- [ROADMAP](../ROADMAP.md)
