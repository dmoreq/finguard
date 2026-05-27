# Finguard

Finguard is organized as a multi-package codebase. The Next.js app lives in `frontend/`; a backend package can be added beside it.

```text
frontend/   Next.js App Router application
supabase/   Database migrations
docs/       Architecture and implementation notes
```

## Local Development

```bash
pnpm --dir frontend install
pnpm frontend:dev
```

Open `http://localhost:3000/chat`.

## Environment

Copy `frontend/.env.example` to `frontend/.env.local`.

Required for the chat UI:

```bash
NEXT_PUBLIC_SUPABASE_URL=
NEXT_PUBLIC_SUPABASE_PUBLISHABLE_KEY=
RASA_URL=http://localhost:5005
```

Sign in at `/login` (email + password). Transactions and chat history are stored in Supabase with RLS.

Optional flags:

- `ENABLE_DEV_USER_FALLBACK=true` + `FIN_GUARD_DEV_USER_ID` — Rasa `sender_id` for API testing without a browser session.
- `ENABLE_LEGACY_AI_PARSE=true` — re-enables deprecated `/api/ai/parse` (OpenAI); production chat should use Rasa only.

Apply database migrations from `supabase/migrations/` to your Supabase project before first use.

## Current Scope

- Next.js App Router chat UI with Supabase Auth (SSR cookies).
- `/api/chat` → Rasa CALM (no OpenAI fallback unless legacy flag is set).
- Dashboard and chat history backed by Supabase Postgres (not `localStorage`).
- Rasa action server persists transactions; frontend syncs from Supabase after each turn.
- Supabase schema and balance RPC in `supabase/migrations/`.
