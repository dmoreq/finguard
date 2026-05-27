# Finguard architecture (hobby stack)

Keep it simple: **Next.js + Rasa CALM + Supabase**. Scale later only if you need to.

## The whole system in one picture

```text
You (browser)
    │
    ▼
Next.js  ──sign in──►  Supabase Auth + Postgres (your data)
    │
    │  POST /api/chat
    ▼
Rasa CALM  ──flows──►  Action server  ──writes──►  Supabase
    │
    └── LLM (via LiteLLM in Docker) for understanding what you said
```

## What each piece does

| Piece | Job |
|-------|-----|
| **Next.js** (`frontend/`) | UI, login, dashboard, proxy chat to Rasa |
| **Supabase** | Users, transactions, chat history; RLS so you only see your rows |
| **Rasa** (`backend/rasa/`) | Conversation flows: record expense, confirm, reports |
| **Action server** (`backend/actions/`) | Python code that inserts/updates rows in Supabase |
| **LiteLLM** (Docker) | Sends Rasa’s LLM calls to Gemini (optional second model later) |

You do **not** need to think about Caddy, Redis, or extra APIs until you deploy for real users.

## Repo layout

```text
frontend/     Next app — start here for UI work
backend/      Rasa + actions — `docker compose up` for local chat brain
supabase/     SQL migrations — run once per Supabase project
docs/         Plans; read this file first, ignore the long review until you need it
```

## Local dev (minimal)

1. Supabase project + run migrations in `supabase/migrations/`.
2. `frontend/.env.local` — Supabase URL/key + `RASA_URL=http://localhost:5005`.
3. `backend/.env` — Supabase service role + LLM keys (see `backend/.env.example`).
4. `cd backend && docker compose up` — Rasa + actions + LiteLLM.
5. `pnpm frontend:dev` → sign in at `/login` → `/chat`.

## Design rules (so it stays simple)

1. **All chat goes through Rasa** — no second “AI parse” path in the app.
2. **Supabase is the database** — not `localStorage`, not a second DB.
3. **Money changes happen in Rasa actions** — not from the browser writing transactions directly (reads via Supabase client are fine).
4. **Add complexity only when it hurts** — e.g. Redis when you run multiple Rasa containers, rate limits when you have abuse.

## When to read more

- **What to build next (full backlog):** [IMPROVEMENT_PLAN.md](./IMPROVEMENT_PLAN.md)
- Day-to-day checkboxes: [IMPLEMENTATION_TRACKER.md](./IMPLEMENTATION_TRACKER.md)
- Deep dive / scorecards rubric: [SYSTEM_DESIGN_REVIEW.md](./SYSTEM_DESIGN_REVIEW.md) (optional)
