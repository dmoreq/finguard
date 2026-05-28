# Architecture Decision Records

We use lightweight ADRs to capture significant technical decisions. Format follows the [adr.github.io](https://adr.github.io/) style.

| ADR | Title | Status |
|-----|-------|--------|
| [001](./001-service-role-in-actions.md) | Service role in action server | Accepted (when Supabase returns) |
| [002](./002-rasa-network-trust.md) | Rasa network trust boundary | Superseded by 003 |
| [003](./003-low-cost-chat-backend.md) | Low-cost chat backend | Accepted (direction) |
| [004](./004-chat-backend-evolution.md) | Chat backend evolution (shipped vs target) | **Accepted** (current) |

When adding a new ADR:

1. Use the next number: `00N-short-title.md`.
2. Include **Status**, **Context**, **Decision**, **Consequences**.
3. Link from [docs/README.md](../README.md) if it affects onboarding or operations.
