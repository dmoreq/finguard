# Local development

No Supabase, no login. **SQLite + localStorage + Python chat backend.**

## Prerequisites

- Node 20+, pnpm
- Python 3.12+, [uv](https://docs.astral.sh/uv/)

## First-time setup

```bash
make setup
```

Edit:

- `frontend/.env.local` — `CHAT_BACKEND_URL=http://127.0.0.1:5055`
- `backend/.env` — copy from `backend/.env.example`

**Backend chat options** (`backend/.env`):

| Variable | Default | Purpose |
|----------|---------|---------|
| `ROUTER_MODE` | `hybrid` | `keyword`, `semantic`, or `hybrid` (first hybrid run may download FastEmbed model) |
| `SEMANTIC_ROUTER_THRESHOLD` | `0.72` | Minimum similarity for semantic intent |
| `LLM_EXTRACT_ENABLED` | `false` | Set `true` + `GEMINI_API_KEY` for LLM slot fill |
| `CI_NO_SEMANTIC` | — | Set in CI to skip embedding-based accuracy test |

**Note:** Server dialogue state is stored in SQLite (`chat_sessions`). Browser chat history remains in `localStorage` only.

## Run

```bash
make dev
```

- Backend: http://127.0.0.1:5055 (chat webhook + data API)
- Frontend: http://localhost:3000

Frontend only (starts backend if :5055 is free):

```bash
make frontend
```

## Verify

```bash
make health
make test
make smoke
```

### Router accuracy (local or CI)

Keyword gate (matches default CI `ROUTER_MODE=keyword`):

```bash
cd backend && uv run python scripts/spike_router.py
```

Hybrid gate (≥95%, downloads FastEmbed model on first run):

```bash
cd backend && ROUTER_MODE=hybrid uv run python scripts/spike_router.py
```

Scheduled CI: [.github/workflows/router-eval.yml](../.github/workflows/router-eval.yml) (Mondays + manual).

### E2E (Playwright)

Local:

```bash
make test-e2e
```

Scheduled CI: [.github/workflows/e2e-nightly.yml](../.github/workflows/e2e-nightly.yml) (daily + manual).

Manual:

- [ ] Record expense in chat → pending card → confirm → sidebar updates
- [ ] Ask "what's my balance this month?"

## Troubleshooting

| Issue | Fix |
|-------|-----|
| 503 on `/api/chat` | Run `make dev`; set `CHAT_BACKEND_URL` in `.env.local` |
| Backend won't start | See `.dev-lite/backend.log` |
| Empty reports | Confirm transactions after recording |
