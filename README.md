# Finguard

Chat to track income and expenses. **Local-first:** Next.js + Rasa + SQLite (no Supabase, no login yet).

```text
frontend/   Next.js UI
backend/    Rasa (Docker) + Python actions + SQLite
```

See **[docs/ARCHITECTURE.md](docs/ARCHITECTURE.md)** and **[docs/runbooks/local-development.md](docs/runbooks/local-development.md)**.

## Quick start

```bash
make setup
# Edit backend/.env (GEMINI_API_KEY) and frontend/.env.local (RASA_URL)
make train    # first time / after flow changes (requires Rasa Pro license)
make dev      # → http://localhost:3000/chat
```

Stop: `Ctrl+C` then `make down`

**Docker** is only for Rasa Pro. Actions and LiteLLM run on the host with `uv`.

## Env

**frontend/.env.local**

```bash
RASA_URL=http://localhost:5005
ACTIONS_URL=http://127.0.0.1:5055
```

**backend/.env**

```bash
GEMINI_API_KEY=
LITELLM_MASTER_KEY=dev-local-key
# Optional: RASA_PRO_LICENSE=   (empty → mock Rasa on :5005)
```

Database file: `backend/data/finguard.db` (created automatically).

Supabase SQL for a future cloud phase: `docs/archive/supabase/migrations/`.
