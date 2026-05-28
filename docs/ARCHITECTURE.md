# Architecture

**Next.js + Python chat backend + local SQLite.** No Supabase or auth until added later.

## System diagram

```text
Browser
    │
    ▼
Next.js (:3000)
    │  POST /api/chat
    │  GET/PATCH /api/data/*
    ▼
Backend FastAPI (:5055)
    ├── POST /webhooks/rest/webhook   → chat (router + FSM + services)
    └── /data/*                       → SQLite CRUD
            │
            ▼
    SQLite (backend/data/finguard.db)
```

Chat history for the UI is stored in **browser localStorage**. Transactions and profile live in **SQLite**.

## Components

| Component | Path | Role |
|-----------|------|------|
| Frontend | `frontend/` | UI, BFF routes, payload mapping |
| Chat package | `backend/actions/chat/` | Intent router, dialogue engine, webhook |
| Services | `backend/actions/services/` | Record, confirm, reports (business logic) |
| Data API | `backend/actions/server.py` | FastAPI app |
| Database | `backend/actions/db/` | Schema, queries, migrations via bootstrap |

## Chat pipeline

1. **Router** (`chat/router.py`) — keyword-based intent (no LLM).
2. **Engine** (`chat/engine.py`) — deterministic FSM: collect fields → pending card → confirm/discard/edit.
3. **Extraction** (`chat/extract/rules.py`) — parse amount, category, period from text.
4. **Services** — validate, write SQLite, return [webhook payloads](./schemas/chat-payloads.json).

Optional `GEMINI_API_KEY` can be wired later for LLM extraction; rule-based parsing works without it.

## API contracts

| Endpoint | Consumer | Notes |
|----------|----------|-------|
| `POST /webhooks/rest/webhook` | Next.js `/api/chat` | Rasa-compatible JSON; see [chat-payloads.json](./schemas/chat-payloads.json) |
| `GET /data/transactions` | Next.js `/api/data/transactions` | List confirmed/pending rows |
| `GET/PATCH /data/profile` | Settings page | Currency, timezone |

Environment: `CHAT_BACKEND_URL` (alias `RASA_URL` deprecated).

## Security (local / hobby)

- Bind backend to localhost in development.
- `/api/chat` rate-limits by user id (in-process).
- Production trust boundary: [ADR-003](./decisions/003-low-cost-chat-backend.md) (supersedes [ADR-002](./decisions/002-rasa-network-trust.md)).

## Related docs

- [runbooks/local-development.md](./runbooks/local-development.md)
- [TEST_STRATEGY.md](./TEST_STRATEGY.md)
- [backend-query-audit.md](./backend-query-audit.md)
- [decisions/003-low-cost-chat-backend.md](./decisions/003-low-cost-chat-backend.md)

## History

Rasa CALM was removed in May 2026. See [archive/low-cost-migration/](./archive/low-cost-migration/) for migration notes.
