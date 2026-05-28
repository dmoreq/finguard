# Log income via chat

| Field | Value |
|-------|-------|
| **Spec ID** | TC-02 |
| **Status** | Shipped |
| **Phase** | MVP |
| **Priority** | Must |
| **Effort** | — |
| **Catalog refs** | TC-02 |

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

Record salary/freelance/bonus as pending income.

## User stories

- As a user, I want this capability so I can manage personal finances through chat without spreadsheets.

## Current state

Shipped in the MVP: behavior is live in backend and/or UI with regression coverage.

## Proposal

Maintain; add VI phrases in 0.5.

## Scope

### In scope

log_income intent + collector.

### Out of scope

Payroll sync.

## Dependencies

TC-01 stack

## Acceptance criteria

- [x] Pending income card
- [ ] VI income phrases

## Risks

Income/expense keyword overlap

## Related

[tc-10-vietnamese-income-chat](./tc-10-vietnamese-income-chat.md)

---

## References

- [USE_CASE_CATALOG](../USE_CASE_CATALOG.md)
- [PRODUCT_PLAN](../PRODUCT_PLAN.md)
- [ROADMAP](../ROADMAP.md)
