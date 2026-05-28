# Gemini JSON extraction

| Field | Value |
|-------|-------|
| **Spec ID** | ENG-GEM |
| **Status** | Shipped |
| **Phase** | P2 |
| **Priority** | Should |
| **Effort** | — |
| **Catalog refs** | ROADMAP P2 |

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

Rules-first Gemini gap-fill for extract.

## User stories

- As a user, I want this capability so I can manage personal finances through chat without spreadsheets.

## Current state

Shipped in the MVP: behavior is live in backend and/or UI with regression coverage.

## Proposal

Keep LLM_EXTRACT_ENABLED off by default.

## Scope

### In scope

CompositeFieldExtractor.

### Out of scope

LLM every message

## Dependencies

extract

## Acceptance criteria

- [x] P2 shipped

## Risks

SDK deprecation

## Related

[tc-08-llm-extract-fallback](./tc-08-llm-extract-fallback.md)

---

## References

- [USE_CASE_CATALOG](../USE_CASE_CATALOG.md)
- [PRODUCT_PLAN](../PRODUCT_PLAN.md)
- [ROADMAP](../ROADMAP.md)
