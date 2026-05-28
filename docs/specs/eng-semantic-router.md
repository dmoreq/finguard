# Semantic Router + hybrid fallback

| Field | Value |
|-------|-------|
| **Spec ID** | ENG-SR |
| **Status** | Shipped |
| **Phase** | P1 |
| **Priority** | Must |
| **Effort** | — |
| **Catalog refs** | ROADMAP P1 |

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

Layer-1 intent routing with ROUTER_MODE hybrid.

## User stories

- As a user, I want this capability so I can manage personal finances through chat without spreadsheets.

## Current state

Shipped in the MVP: behavior is live in backend and/or UI with regression coverage.

## Proposal

Maintain ≥95% utterances.jsonl hybrid locally.

## Scope

### In scope

Semantic + keyword routes.

### Out of scope

LLM routing

## Dependencies

router

## Acceptance criteria

- [x] P1 shipped

## Risks

Keyword CI ≠ hybrid

## Related

[v-07-hybrid-router-vi-eval](./v-07-hybrid-router-vi-eval.md)

---

## References

- [USE_CASE_CATALOG](../USE_CASE_CATALOG.md)
- [PRODUCT_PLAN](../PRODUCT_PLAN.md)
- [ROADMAP](../ROADMAP.md)
