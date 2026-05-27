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

The app can run without `OPENAI_API_KEY`; `/api/ai/parse` falls back to a deterministic parser for local development. Add `OPENAI_API_KEY` and `AI_MODEL` to use the server-side structured AI path.

Supabase environment variables are prepared for the next persistence/auth phase:

```bash
NEXT_PUBLIC_SUPABASE_URL=
NEXT_PUBLIC_SUPABASE_PUBLISHABLE_KEY=
```

## Current Scope

- Next.js App Router shell.
- Chat-driven transaction entry.
- Server-side parse route.
- Confirmation/edit card.
- Dashboard/report panel.
- Local browser persistence until Supabase auth is connected.
- Supabase initial schema migration in `supabase/migrations`.
