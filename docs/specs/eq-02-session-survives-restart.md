# Session survives restart

| Field | Value |
|-------|-------|
| **Spec ID** | EQ-02 |
| **Status** | Shipped |
| **Phase** | P2 |
| **Priority** | Must |
| **Effort** | — |
| **Catalog refs** | EQ-02 |

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

Pending not lost on restart.

## User stories

- As a user, I want this capability so I can manage personal finances through chat without spreadsheets.

## Current state

Shipped in the MVP: behavior is live in backend and/or UI with regression coverage.

## Proposal

SQLite chat_sessions (shipped P2).

## Scope

### In scope

Session persist tests.

### Out of scope

—

## Dependencies

eng-sqlite-sessions.md

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
