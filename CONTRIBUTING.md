# Contributing to Finguard

Thanks for your interest in contributing. This project is a monorepo with a **Next.js** frontend and a **Python (FastAPI)** backend.

## Prerequisites

- Node 20+ and [pnpm](https://pnpm.io/)
- Python 3.12+ and [uv](https://docs.astral.sh/uv/)
- macOS/Linux (primary dev target)

## Getting started

```bash
make setup
cp frontend/.env.example frontend/.env.local
cp backend/.env.example backend/.env
# Set CHAT_BACKEND_URL=http://127.0.0.1:5055 in frontend/.env.local
make dev
```

See [docs/runbooks/local-development.md](docs/runbooks/local-development.md) for details.

Planned chat-backend work (Burr, DuckDB, semantic router): [docs/ROADMAP.md](docs/ROADMAP.md).

## Development workflow

1. Create a branch from `main`.
2. Make focused changes; keep PRs reviewable (~300 lines or less when possible).
3. Run checks before opening a PR:

```bash
make test          # Vitest + pytest
make lint          # Biome + ruff
make smoke         # optional stack smoke
```

4. Follow [Conventional Commits](https://www.conventionalcommits.org/) for commit messages, e.g. `feat(backend): add spending filter`.

## Tests

- **Required** for behavior changes: add or update tests at the lowest useful layer (see [docs/TEST_STRATEGY.md](docs/TEST_STRATEGY.md)).
- Frontend: colocate `*.test.ts` next to source.
- Backend: `backend/tests/` mirroring `actions/`.

## Documentation

- Update [docs/ARCHITECTURE.md](docs/ARCHITECTURE.md) for structural changes.
- Add an ADR under [docs/decisions/](docs/decisions/) for significant technical choices.
- Do not edit files under [docs/archive/](docs/archive/) except to add a superseded notice.

## Pull requests

- Describe **what** and **why** in the PR body.
- Link related issues if any.
- Ensure CI passes (GitHub Actions on push/PR).

## Code style

- Python: `ruff` (format + lint), `pyright` — run via pre-commit or `make lint`.
- TypeScript: `biome` — run via pre-commit or `pnpm exec biome check` in `frontend/`.

## Questions

Open a GitHub issue for bugs or feature discussion. For security concerns, avoid posting secrets in public issues.
