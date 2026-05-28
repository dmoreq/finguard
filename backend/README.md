# Finguard backend

Rasa CALM assistant + Python action server.

## Lite local (default)

Only **Rasa** uses Docker. Actions and LiteLLM run on the host:

```bash
# From repo root
make dev
```

Or manually:

```bash
cd backend
uv sync
uv run uvicorn actions.server:app --host 127.0.0.1 --port 5055
uv run litellm --config litellm/config.yaml --port 4000
docker compose up -d    # Rasa on :5005
```

## Commands

| Command | Description |
|---------|-------------|
| `make train` | Train model (from repo root) |
| `make down` | Stop all lite processes |
| `uv run pytest tests/ -q` | Unit tests |

See [docs/runbooks/local-development.md](../docs/runbooks/local-development.md).
