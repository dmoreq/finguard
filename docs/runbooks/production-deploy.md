# Production deploy runbook (scale tier)

Use when moving beyond local hobby setup. For day-to-day development see [local-development.md](./local-development.md).

## Topology

```text
Users → Vercel (Next.js) → private network → VPS (Rasa + actions + LiteLLM)
                ↓
           Supabase (hosted Postgres + Auth)
```

## Checklist

1. **Supabase** — Create production project; apply all files in `supabase/migrations/`; enable email auth.
2. **Secrets** — `NEXT_PUBLIC_SUPABASE_*` on Vercel; `SUPABASE_SERVICE_ROLE_KEY` only on the action server.
3. **Rasa VPS** — `docker compose up -d`; train model; do **not** expose port 5005 to `0.0.0.0` without a firewall rule for the Next server IP only.
4. **Vercel** — Set `RASA_URL` to the private URL reachable from Vercel (VPN, Tailscale, or public IP + firewall).
5. **Rate limits** — Replace in-process limit in `server/chat/rate-limit.ts` with Upstash/Vercel KV (see IMPROVEMENT_PLAN SEC-6).
6. **Redis tracker** — Optional when running multiple Rasa replicas (`backend/docker-compose.yml` tracker store).
7. **Smoke** — Run `scripts/smoke-e2e.sh` against staging URLs after deploy.

## Rollback

- Vercel: redeploy previous build.
- Rasa: keep previous trained model tag in Docker volume; `docker compose restart rasa`.
- Database: forward-only migrations; restore from Supabase backup if needed.
