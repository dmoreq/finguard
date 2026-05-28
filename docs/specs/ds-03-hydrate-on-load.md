# Hydrate transactions on load

| Field | Value |
|-------|-------|
| **Spec ID** | DS-03 |
| **Status** | Shipped |
| **Phase** | MVP |
| **Priority** | Must |
| **Effort** | — |
| **Catalog refs** | DS-03 |

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

Sidebar and chat sync transactions on app load.

## User stories

- As a user, I want this capability so I can manage personal finances through chat without spreadsheets.

## Current state

Shipped in the MVP: behavior is live in backend and/or UI with regression coverage.

## Proposal

Maintain hydrate on startup.

## Scope

### In scope

Fetch txs on load.

### Out of scope

—

## Dependencies

API client

## Acceptance criteria

- [x] CP-4 partial

## Risks

—

## Related

[cm-04-transaction-list-ui](./cm-04-transaction-list-ui.md)

---

## References

- [USE_CASE_CATALOG](../USE_CASE_CATALOG.md)
- [PRODUCT_PLAN](../PRODUCT_PLAN.md)
- [ROADMAP](../ROADMAP.md)
