# Production deploy (future)

This project is **local-first** today. Use [local-development.md](./local-development.md) for daily work.

When you deploy to a hosted environment, expect roughly:

```text
Users → Vercel (Next.js) → private network → VPS or container (Python backend)
                ↓
           Optional: Supabase (Postgres + Auth) — see docs/archive/supabase/
```

## Checklist (draft)

1. **Backend** — Run `uvicorn actions.server:app` behind a reverse proxy; do not expose SQLite file to the internet; plan Postgres if multi-user.
2. **Next.js** — Set `CHAT_BACKEND_URL` and `ACTIONS_URL` to the private backend URL (same host in simple setups).
3. **Secrets** — `GEMINI_API_KEY` on backend only if using cloud LLM extraction.
4. **Firewall** — Only the Next.js host (or edge) may reach the chat webhook; see [ADR-003](../decisions/003-low-cost-chat-backend.md).
5. **Rate limits** — Replace in-process limit in `frontend/src/server/chat/rate-limit.ts` with Redis/Upstash at scale.
6. **Smoke** — Run `scripts/smoke-e2e.sh` against staging URLs.

## Supabase path

If reintroducing Supabase:

- Apply migrations under [docs/archive/supabase/migrations/](../archive/supabase/migrations/).
- Follow [ADR-001](../decisions/001-service-role-in-actions.md) for service-role usage.

## Rollback

- Redeploy previous Vercel build.
- Backend: redeploy previous container image; SQLite/Postgres restore from backup if needed.
