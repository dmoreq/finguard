# Relative dates (today/yesterday)

| Field | Value |
|-------|-------|
| **Spec ID** | TC-07 |
| **Status** | Partial |
| **Phase** | MVP |
| **Priority** | Should |
| **Effort** | S |
| **Catalog refs** | TC-07 |

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

hôm qua / yesterday in chat.

## User stories

- As a user, I want this capability so I can manage personal finances through chat without spreadsheets.

## Current state

Partially implemented: core path exists but gaps limit daily use or Vietnamese coverage.

## Proposal

VI date tokens + timezone.

## Scope

### In scope

Common relative dates.

### Out of scope

Complex NL dates.

## Dependencies

ST-03

## Acceptance criteria

- [x] EN yesterday
- [ ] hôm nay/hôm qua

## Risks

TZ boundaries

## Related

[st-03-timezone-setting](./st-03-timezone-setting.md)

---

## References

- [USE_CASE_CATALOG](../USE_CASE_CATALOG.md)
- [PRODUCT_PLAN](../PRODUCT_PLAN.md)
- [ROADMAP](../ROADMAP.md)
