# ADR-002: Rasa network trust boundary

## Status

Superseded by [003-low-cost-chat-backend.md](./003-low-cost-chat-backend.md)

## Date

2026-05-27

## Context

`/api/chat` proxies user messages to Rasa’s REST webhook. If Rasa is exposed on the public internet without authentication, anyone could drive flows and trigger actions.

## Decision

**Hobby:** Run Rasa on localhost or a private Docker network; set `RASA_URL` only on the Next.js server.

**Production (when deployed):** Do not publish Rasa ports publicly. Restrict ingress to the Next.js host IP. Optionally add `RASA_WEBHOOK_SECRET` checked by a reverse proxy or custom middleware.

## Consequences

- Vercel-hosted Next cannot call a laptop Rasa — need a VPS or tunnel for integrated demos.
- Rate limiting on `/api/chat` (in-process for hobby; Redis/Upstash at scale) limits abuse of the BFF even when Rasa is private.
