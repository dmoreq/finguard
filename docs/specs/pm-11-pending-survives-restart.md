# Pending survives backend restart

| Field | Value |
|-------|-------|
| **Spec ID** | PM-11 |
| **Status** | Shipped |
| **Phase** | P2 |
| **Priority** | Must |
| **Effort** | — |
| **Catalog refs** | PM-11 |

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

Pending and collecting state restored after backend restart.

## User stories

- As a user, I want this capability so I can manage personal finances through chat without spreadsheets.

## Current state

Shipped in the MVP: behavior is live in backend and/or UI with regression coverage.

## Proposal

Maintain SQLite chat_sessions persistence.

## Scope

### In scope

Session restore for pending flows.

### Out of scope

Cross-device sync.

## Dependencies

eng-sqlite-sessions.md

## Acceptance criteria

- [x] test_session_persist.py

## Risks

—

## Related

[eng-sqlite-sessions](./eng-sqlite-sessions.md), [eq-02-session-survives-restart](./eq-02-session-survives-restart.md)

---

## References

- [USE_CASE_CATALOG](../USE_CASE_CATALOG.md)
- [PRODUCT_PLAN](../PRODUCT_PLAN.md)
- [ROADMAP](../ROADMAP.md)
