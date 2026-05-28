# Finguard architecture

**Next.js + low-cost Python chat backend + local SQLite.** No Supabase or auth until you add them later.

## The whole system in one picture

```text
You (browser)
    │
    ▼
Next.js  ──/api/data/*──►  Backend (FastAPI) :5055  ──►  SQLite (backend/data/)
    │
    │  POST /api/chat
    ▼
Backend  ──Semantic Router + FSM + rules/LLM extract──►  same SQLite
```

Chat uses a **keyword router** and **deterministic dialogue engine** (no Rasa CALM, no Pro license). Optional `GEMINI_API_KEY` improves extraction; rule-based parsing works offline.

## What each piece does

| Piece | Job |
|-------|-----|
| **Next.js** (`frontend/`) | UI, `/api/chat` → backend webhook, `/api/data/*` → backend data API |
| **Backend** (`backend/actions/`) | `POST /webhooks/rest/webhook` (chat) + `/data/*` (CRUD) |
| **SQLite** | Transactions and profile (`backend/data/finguard.db`) |
| **Chat package** (`actions/chat/`) | Router, FSM (`engine.py`), rule extraction |
| **Services** (`actions/services/`) | Record, confirm, reports (no Rasa SDK) |

## Repo layout

```text
frontend/     Next app
backend/      Python backend (chat + data API)
docs/         Architecture, runbooks, plans
```

## Local dev

```bash
make dev
```

Set `CHAT_BACKEND_URL=http://127.0.0.1:5055` in `frontend/.env.local`.

See [runbooks/local-development.md](./runbooks/local-development.md).

## Migration note

Rasa CALM artifacts were removed in favor of [LOW_COST_IMPLEMENTATION_PLAN.md](./LOW_COST_IMPLEMENTATION_PLAN.md). Historical Rasa docs live under `docs/archive/`.

## More docs

- [low_cost_plan.md](./low_cost_plan.md) — design rationale
- [LOW_COST_IMPLEMENTATION_PLAN.md](./LOW_COST_IMPLEMENTATION_PLAN.md) — execution plan
- [TEST_STRATEGY.md](./TEST_STRATEGY.md) — QA plan
- [decisions/003-low-cost-chat-backend.md](./decisions/003-low-cost-chat-backend.md) — ADR
