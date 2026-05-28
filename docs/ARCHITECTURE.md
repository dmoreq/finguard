# Finguard architecture

**Next.js + Rasa CALM + local SQLite.** No Supabase or auth until you add them later.

## The whole system in one picture

```text
You (browser)
    │
    ▼
Next.js  ──/api/data/*──►  Action server (FastAPI)  ──►  SQLite (backend/data/)
    │
    │  POST /api/chat
    ▼
Rasa CALM  ──flows──►  Action server (custom actions)
    │
    └── LLM via LiteLLM (host) when RASA_PRO_LICENSE is set
        or mock-rasa.py locally without a license
```

Chat messages persist in **browser localStorage** for now. Transactions and profile live in **SQLite**.

## What each piece does

| Piece | Job |
|-------|-----|
| **Next.js** (`frontend/`) | UI, `/api/chat` → Rasa, `/api/data/*` → action server |
| **Action server** (`backend/actions/`) | Rasa custom actions + REST reads for the UI |
| **SQLite** | Transactions and profile (`backend/data/finguard.db`) |
| **Rasa** (`backend/rasa/`) | CALM flows: record, confirm, reports |
| **LiteLLM** (host, optional) | LLM routing when using Rasa Pro |

## Repo layout

```text
frontend/     Next app
backend/      Rasa config + Python actions
docs/         Architecture, runbooks, archive/
docs/archive/supabase/   Deferred Postgres migrations
```

## Local dev

```bash
make dev
```

See [runbooks/local-development.md](./runbooks/local-development.md).

## When to add Supabase again

1. Multi-user auth and hosted Postgres.
2. Apply archived migrations under `docs/archive/supabase/migrations/`.
3. Add Supabase auth to Next.js; see [decisions/001-service-role-in-actions.md](./decisions/001-service-role-in-actions.md).

## More docs

- [IMPLEMENTATION_TRACKER.md](./IMPLEMENTATION_TRACKER.md) — status
- [TEST_STRATEGY.md](./TEST_STRATEGY.md) — QA plan
- [CLEANUP_PLAN.md](./CLEANUP_PLAN.md) — legacy removal log
- [archive/](./archive/) — superseded planning docs
