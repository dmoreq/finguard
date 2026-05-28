# Finguard backend

Unified **FastAPI** app: chat webhook + SQLite data API.

## Run

```bash
uv sync
uv run uvicorn actions.server:app --host 127.0.0.1 --port 5055 --reload
```

## Endpoints

| Method | Path | Purpose |
|--------|------|---------|
| GET | `/health` | Health check |
| POST | `/webhooks/rest/webhook` | Chat (Rasa-compatible JSON) |
| GET | `/data/transactions` | List transactions |
| GET/PATCH | `/data/profile` | User profile |

## Tests

```bash
uv run pytest tests/ -q
uv run python scripts/spike_router.py
```

## Layout

- `actions/chat/` — router, dialogue engine, webhook
- `actions/services/` — business logic
- `actions/db/` — SQLite
