# Enable/disable LLM extraction (UI)

| Field | Value |
|-------|-------|
| **Spec ID** | ST-06 |
| **Status** | Partial |
| **Phase** | MVP |
| **Priority** | Could |
| **Effort** | S |
| **Catalog refs** | ST-06 |

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

User controls LLM extract without env vars.

## User stories

- As a user, I want this capability so I can manage personal finances through chat without spreadsheets.

## Current state

Partially implemented: core path exists but gaps limit daily use or Vietnamese coverage.

## Proposal

Add Settings toggle wired to backend flag.

## Scope

### In scope

UI toggle for LLM_EXTRACT.

### Out of scope

Per-message override.

## Dependencies

TC-08

## Acceptance criteria

- [ ] Toggle persists preference

## Risks

Env-only today

## Related

[tc-08-llm-extract-fallback](./tc-08-llm-extract-fallback.md)

---

## References

- [USE_CASE_CATALOG](../USE_CASE_CATALOG.md)
- [PRODUCT_PLAN](../PRODUCT_PLAN.md)
- [ROADMAP](../ROADMAP.md)
