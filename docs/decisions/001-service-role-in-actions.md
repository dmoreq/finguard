# ADR-001: Service role in Rasa actions

## Status

Accepted

## Date

2026-05-27

## Context

Money mutations (create, confirm, discard transactions) must be reliable and must not trust the browser to write arbitrary rows. Supabase Row Level Security protects direct client access, but Rasa actions need to update any row for the authenticated user when flows complete.

## Decision

Use the Supabase **service role** key only inside the Python action server. Every query in `actions/db/queries.py` includes `user_id` from Rasa slots (set from Next.js `metadata.user_id` at session start).

The Next.js app uses the anon/publishable key with the user session for reads (chat history, transaction list) and never performs transaction mutations directly.

## Consequences

- Compromised Rasa or action server credentials are high impact — keep Docker network local in development and firewall in production.
- Slot injection bugs could target wrong users — validate `user_id` on every mutation and in tests.
- No dual-write paths; Rasa is the only writer for transaction state changes.
