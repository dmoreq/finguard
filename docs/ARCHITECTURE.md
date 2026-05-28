# Architecture

**Next.js + Python chat backend + local SQLite.** No Supabase or auth until added later.

This page describes the **as-built** system. For the **target** four-layer stack and **backlog** (including Burr and DuckDB), see [design/chat-backend-target.md](./design/chat-backend-target.md) and [ROADMAP.md](./ROADMAP.md).

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

## Chat pipeline (four layers, as shipped)

| Layer | Module | Role |
|-------|--------|------|
| 1 — Routing | `chat/router.py` | Keyword/regex intent (no LLM) |
| 2 — Dialogue | `chat/engine.py` | FSM: collect → pending card → confirm / discard / edit |
| 3 — Extraction | `chat/extract/rules.py` | Amount, category, period from text |
| 4 — Data | `services/*` | SQLite writes/reads; [webhook payloads](./schemas/chat-payloads.json) |

`GEMINI_API_KEY` is optional for future Outlines-based extraction; rules work without it.

### Current vs target

| Layer | Shipped | Target / backlog |
|-------|---------|------------------|
| 1 | Keyword router | Semantic Router — [ROADMAP P1](./ROADMAP.md) |
| 2 | `engine.py` | **Burr** — [ROADMAP P3](./ROADMAP.md#burr-backlog-detail) |
| 3 | Rules | Outlines + Gemini (fallback) — [ROADMAP P2](./ROADMAP.md) |
| 4 | SQLite + services | + **DuckDB** for analytics — [ROADMAP P4](./ROADMAP.md#duckdb-backlog-detail) |

See [ADR-004](./decisions/004-chat-backend-evolution.md).

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

| Doc | Role |
|-----|------|
| [ROADMAP.md](./ROADMAP.md) | Backlog (Burr, DuckDB, semantic router, Outlines) |
| [design/chat-backend-target.md](./design/chat-backend-target.md) | Target architecture |
| [runbooks/local-development.md](./runbooks/local-development.md) | Local dev |
| [TEST_STRATEGY.md](./TEST_STRATEGY.md) | Testing |
| [backend-query-audit.md](./backend-query-audit.md) | SQLite `user_id` rules |
| [decisions/003](./decisions/003-low-cost-chat-backend.md) · [004](./decisions/004-chat-backend-evolution.md) | ADRs |

## History

Rasa CALM was removed in May 2026. See [archive/low-cost-migration/](./archive/low-cost-migration/) for migration notes.
