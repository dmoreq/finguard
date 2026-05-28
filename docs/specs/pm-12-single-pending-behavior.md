# One pending at a time

| Field | Value |
|-------|-------|
| **Spec ID** | PM-12 |
| **Status** | Partial |
| **Phase** | MVP |
| **Priority** | Should |
| **Effort** | S |
| **Catalog refs** | PM-12 |

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

Clear behavior when user starts a new expense while another is pending.

## User stories

- As a user, I want this capability so I can manage personal finances through chat without spreadsheets.

## Current state

Partially implemented: core path exists but gaps limit daily use or Vietnamese coverage.

## Proposal

Document and test replace-or-block policy.

## Scope

### In scope

Explicit UX for pending conflict.

### Out of scope

Multiple simultaneous pending cards.

## Dependencies

DialogueEngine

## Acceptance criteria

- [ ] Documented + tested conflict

## Risks

Implicit behavior today

## Related

[pm-01-pending-card-review](./pm-01-pending-card-review.md)

---

## References

- [USE_CASE_CATALOG](../USE_CASE_CATALOG.md)
- [PRODUCT_PLAN](../PRODUCT_PLAN.md)
- [ROADMAP](../ROADMAP.md)
