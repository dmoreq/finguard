# SQLite chat_sessions persistence

| Field | Value |
|-------|-------|
| **Spec ID** | ENG-SES |
| **Status** | Shipped |
| **Phase** | P2 |
| **Priority** | Must |
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

Persist dialogue phase and pending across restarts.

## User stories

- As a user, I want this capability so I can manage personal finances through chat without spreadsheets.

## Current state

Shipped in the MVP: behavior is live in backend and/or UI with regression coverage.

## Proposal

Maintain chat_sessions table.

## Scope

### In scope

Session persist.

### Out of scope

Postgres sessions

## Dependencies

sessions

## Acceptance criteria

- [x] test_session_persist

## Risks

—

## Related

[pm-11-pending-survives-restart](./pm-11-pending-survives-restart.md)

---

## References

- [USE_CASE_CATALOG](../USE_CASE_CATALOG.md)
- [PRODUCT_PLAN](../PRODUCT_PLAN.md)
- [ROADMAP](../ROADMAP.md)
