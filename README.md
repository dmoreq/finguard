# Finguard

Chat to track income and expenses. **Local-first:** Next.js + Python chat backend + SQLite (no Supabase, no login yet).

## Stack

```text
frontend/    Next.js UI
backend/     FastAPI chat + data API, SQLite
```

## Quick start

```bash
make setup
# Edit frontend/.env.local (CHAT_BACKEND_URL=http://127.0.0.1:5055)
make dev
```

Open http://localhost:3000

**No Docker or Rasa license required.**

## Environment

`frontend/.env.local`:

```env
CHAT_BACKEND_URL=http://127.0.0.1:5055
ACTIONS_URL=http://127.0.0.1:5055
```

Optional `backend/.env`: `GEMINI_API_KEY` for richer slot extraction.

## Commands

| Command | Description |
|---------|-------------|
| `make dev` | Backend + Next.js |
| `make test` | Vitest + pytest |
| `make smoke` | Tests + webhook smoke |
| `make down` | Stop local processes |

## Docs

- [docs/ARCHITECTURE.md](docs/ARCHITECTURE.md)
- [docs/runbooks/local-development.md](docs/runbooks/local-development.md)
