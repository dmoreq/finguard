# Distributed rate limiting

| Field | Value |
|-------|-------|
| **Spec ID** | AU-08 |
| **Status** | Planned |
| **Phase** | 4 |
| **Priority** | Should (scale) |
| **Effort** | M |
| **Catalog refs** | AU-08, U-4 |

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

Redis/Upstash rate limits multi-instance.

## User stories

- As a user, I want this capability so I can manage personal finances through chat without spreadsheets.

## Current state

Planned in PRODUCT_PLAN with a phase ID; design agreed, implementation not complete.

## Proposal

When scaling beyond single node.

## Scope

### In scope

Distributed 429.

### Out of scope

Single-node limit OK now

## Dependencies

ux-05-rate-limit-message.md

## Acceptance criteria

TBD

## Risks

Cost

## Related

[ux-05-rate-limit-message](./ux-05-rate-limit-message.md)

---

## References

- [USE_CASE_CATALOG](../USE_CASE_CATALOG.md)
- [PRODUCT_PLAN](../PRODUCT_PLAN.md)
- [ROADMAP](../ROADMAP.md)
