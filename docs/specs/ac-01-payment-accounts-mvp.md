# Payment accounts MVP

| Field | Value |
|-------|-------|
| **Spec ID** | AC-01 |
| **Status** | Planned |
| **Phase** | 1.5 |
| **Priority** | Should |
| **Effort** | L |
| **Catalog refs** | AC-01 |

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

Track cash, bank, e-wallet accounts; assign txs to account.

## User stories

- As a user, I want this capability so I can manage personal finances through chat without spreadsheets.

## Current state

Planned in PRODUCT_PLAN with a phase ID; design agreed, implementation not complete.

## Proposal

Accounts table + optional account on record; chat mention later.

## Scope

### In scope

CRUD accounts, default account, tx.account_id.

### Out of scope

Full open banking.

## Dependencies

schema migration

## Acceptance criteria

TBD

## Risks

Scope vs Phase 0.5

## Related

[ac-04-spending-by-account-report](./ac-04-spending-by-account-report.md)

---

## References

- [USE_CASE_CATALOG](../USE_CASE_CATALOG.md)
- [PRODUCT_PLAN](../PRODUCT_PLAN.md)
- [ROADMAP](../ROADMAP.md)
