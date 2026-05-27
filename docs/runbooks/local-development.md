# Local development runbook

Stack: **Next.js** + **Rasa CALM** + **Supabase**. See [ARCHITECTURE.md](../ARCHITECTURE.md).

## Prerequisites

- Node 22+, pnpm
- Python 3.12+, [uv](https://docs.astral.sh/uv/)
- Docker Desktop (for Rasa + LiteLLM + action server)
- Supabase project (free tier is fine)

## 1. Database

1. Create a project at [supabase.com](https://supabase.com).
2. Run SQL from `supabase/migrations/` in order (SQL editor or CLI):
   - `20260527000000_initial_schema.sql`
   - `20260527000001_balance_rpc.sql`
   - `20260528000000_profile_on_signup.sql`
3. Note **Project URL**, **anon key**, and **service role key**.

## 2. Backend (Rasa stack)

```bash
cp backend/.env.example backend/.env
# Fill: SUPABASE_URL, SUPABASE_SERVICE_ROLE_KEY, GEMINI_API_KEY, LITELLM_MASTER_KEY

cd backend
docker compose build
docker compose run --rm rasa train   # first time / after flow changes
docker compose up
```

Health checks:

- Actions: http://localhost:5055/health
- Rasa: http://localhost:5005/status
- LiteLLM: http://localhost:4000/health (needs keys in `.env`)

Smoke script (repo root):

```bash
chmod +x scripts/smoke-e2e.sh
./scripts/smoke-e2e.sh
```

## 3. Frontend

```bash
cp frontend/.env.example frontend/.env.local
# Fill: NEXT_PUBLIC_SUPABASE_URL, NEXT_PUBLIC_SUPABASE_PUBLISHABLE_KEY
# RASA_URL=http://localhost:5005

pnpm --dir frontend install
pnpm frontend:dev
```

Open http://localhost:3000 → **Sign up** at `/login` → `/chat`.

## 4. Happy path checklist

- [ ] Sign up with email/password
- [ ] Send: `Spent $10 on coffee`
- [ ] See pending transaction card
- [ ] Confirm
- [ ] Row in Supabase `transactions` with `status = confirmed`
- [ ] Dashboard sidebar shows the expense

## Troubleshooting

| Problem | Fix |
|---------|-----|
| 401 on chat | Sign in; check Supabase keys in `.env.local` |
| 503 Rasa not configured | Set `RASA_URL`; start `docker compose up` |
| No profile / defaults only | Apply `20260528000000_profile_on_signup.sql` |
| Rasa empty replies | Run `docker compose run --rm rasa train` |
| Actions DB errors | Check `SUPABASE_SERVICE_ROLE_KEY` in `backend/.env` |
