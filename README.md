# Finguard

Chat to track income and expenses. **Local-first:** Next.js, Python backend, SQLite — no cloud auth required for development.

## Features

- Natural language expense and income logging
- Confirm-or-edit pending transaction cards
- Balance and spending summaries
- Local SQLite storage; chat history in browser storage

## Quick start

```bash
make setup
cp frontend/.env.example frontend/.env.local
# Set CHAT_BACKEND_URL=http://127.0.0.1:5055
make dev
```

Open [http://localhost:3000](http://localhost:3000).

## Stack

| Layer | Technology |
|-------|------------|
| Frontend | Next.js, TypeScript |
| Backend | FastAPI, Python 3.12 |
| Database | SQLite (`backend/data/`) |

No Docker or paid licenses required for local development.

## Configuration

`frontend/.env.local`:

```env
CHAT_BACKEND_URL=http://127.0.0.1:5055
ACTIONS_URL=http://127.0.0.1:5055
```

Optional `backend/.env`: `GEMINI_API_KEY` for future LLM-based extraction.

## Commands

| Command | Description |
|---------|-------------|
| `make dev` | Backend + Next.js |
| `make test` | Vitest + pytest |
| `make smoke` | Tests + webhook smoke |
| `make lint` | Biome + ruff |
| `make down` | Stop local processes |

## Documentation

| Doc | Description |
|-----|-------------|
| [docs/README.md](docs/README.md) | Documentation index |
| [docs/ARCHITECTURE.md](docs/ARCHITECTURE.md) | System design |
| [docs/runbooks/local-development.md](docs/runbooks/local-development.md) | Local dev runbook |
| [docs/TEST_STRATEGY.md](docs/TEST_STRATEGY.md) | Testing approach |
| [CONTRIBUTING.md](CONTRIBUTING.md) | How to contribute |

## Project structure

```text
frontend/     Next.js application
backend/      Python chat + data API
docs/         Architecture, ADRs, runbooks
```

## License

See repository license file (if present). Otherwise treat as private project.
