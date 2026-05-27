# Finguard

Hobby project: chat to track income and expenses. Stack is **Next.js + Rasa CALM + Supabase**.

See **[docs/ARCHITECTURE.md](docs/ARCHITECTURE.md)** for the stack overview and **[docs/IMPROVEMENT_PLAN.md](docs/IMPROVEMENT_PLAN.md)** for the full improvement backlog.

> **Note:** An earlier browser-only prototype may exist outside this repo; this monorepo is the maintained product (Next + Rasa + Supabase).

```text
frontend/   Next.js app (UI + /api/chat → Rasa)
backend/    Rasa CALM + action server (Docker)
supabase/   Postgres migrations
```

## Quick start

```bash
# Frontend
cp frontend/.env.example frontend/.env.local   # fill Supabase + RASA_URL
pnpm --dir frontend install
pnpm frontend:dev

# Backend (separate terminal)
cp backend/.env.example backend/.env           # fill keys
cd backend && docker compose up
```

Open http://localhost:3000 → sign in → `/chat`.

Apply SQL in `supabase/migrations/` to your Supabase project before first use.

## Env (frontend)

```bash
NEXT_PUBLIC_SUPABASE_URL=
NEXT_PUBLIC_SUPABASE_PUBLISHABLE_KEY=
RASA_URL=http://localhost:5005
```

Backend needs Supabase **service role** and LLM keys for Docker — see `backend/.env.example`.
