# Finguard backend (Rasa CALM + actions)

Python action server and Rasa assistant for chat-driven finance tracking.

## Prerequisites

- [uv](https://docs.astral.sh/uv/) for Python deps
- Docker for Rasa, LiteLLM, and the action server
- Supabase project with migrations applied (`../supabase/migrations/`)

## Setup

```bash
cp .env.example .env   # service role + LLM keys
uv sync
```

## Commands

| Command | Description |
|---------|-------------|
| `uv run pytest tests/ -q` | Unit tests (mocked Supabase) |
| `uv run ruff check actions tests` | Lint |
| `uv run pyright` | Typecheck |
| `docker compose up` | Rasa + actions + LiteLLM |
| `docker compose run --rm rasa train` | Train CALM model |

## Architecture

- **Flows** in `rasa/data/` — CALM conversation logic
- **Handlers** in `actions/handlers/` — Supabase mutations (service role)
- **Queries** in `actions/db/queries.py` — every query scoped by `user_id`

See `docs/decisions/001-service-role-in-actions.md` and `docs/ARCHITECTURE.md`.

## websockets override

`pyproject.toml` pins compatible `websockets` for the Rasa SDK — do not remove without checking `uv lock`.
