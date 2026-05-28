# Low-cost backend migration (archived)

**Status:** Completed 2026-05-28

Migration from **Rasa CALM + Rasa Pro** to the in-repo **keyword router + dialogue engine + services** stack.

**Current docs:** [ARCHITECTURE.md](../../ARCHITECTURE.md) · [ROADMAP.md](../../ROADMAP.md) · [design/chat-backend-target.md](../../design/chat-backend-target.md) · [ADR-003](../../decisions/003-low-cost-chat-backend.md) · [ADR-004](../../decisions/004-chat-backend-evolution.md)

| File | Contents |
|------|----------|
| [implementation-plan.md](./implementation-plan.md) | Phased checklist and Rasa decommission list (historical) |

**Supabase → SQLite cleanup** was executed 2026-05-28 (removed legacy frontend/backend paths; Supabase SQL archived under [../supabase/](../supabase/)).
