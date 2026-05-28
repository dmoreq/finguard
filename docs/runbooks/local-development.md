# Local development

No Supabase, no login. **SQLite + localStorage + Rasa.**

See [ARCHITECTURE.md](../ARCHITECTURE.md).

## Prerequisites

- Node 22+, pnpm
- Python 3.12+, uv
- Docker Desktop (Rasa Pro only; mock Rasa needs no Docker)
- `GEMINI_API_KEY` in `backend/.env` (for `make train` with Rasa Pro)

## Start

```bash
make setup
make train    # first time / after flow changes (Rasa Pro license required)
make dev      # → http://localhost:3000/chat
```

Stop: `Ctrl+C` then `make down`

Frontend only (starts action server + mock Rasa if ports are free):

```bash
pnpm frontend:dev
```

## Env

**frontend/.env.local**

```bash
RASA_URL=http://localhost:5005
ACTIONS_URL=http://127.0.0.1:5055
```

**backend/.env**

```bash
GEMINI_API_KEY=your-key
LITELLM_MASTER_KEY=dev-local-key
# RASA_PRO_LICENSE=   # leave empty for mock Rasa on :5005
```

## Data files

| What | Location |
|------|----------|
| Transactions, profile | `backend/data/finguard.db` |
| Chat messages | Browser `localStorage` |

## Health

```bash
make health
# or
./scripts/check-health.sh
```

## Happy path

- [ ] Open http://localhost:3000/chat
- [ ] Send: `Spent $10 on coffee`
- [ ] See pending transaction card (mock or CALM)
- [ ] Confirm in UI
- [ ] Transaction appears in sidebar

## Troubleshooting

| Problem | Fix |
|---------|-----|
| `ERR_CONNECTION_REFUSED` on `/api/data/*` | Run `make dev` or `pnpm frontend:dev` (starts action server) |
| 503 on `/api/chat` | Start mock Rasa or `make dev`; check `RASA_URL` |
| Rasa Pro won't start | Set `RASA_PRO_LICENSE` or use mock mode (empty license) |
| Port 5055 in use | `make down`; kill stale `uvicorn` / Docker containers |
