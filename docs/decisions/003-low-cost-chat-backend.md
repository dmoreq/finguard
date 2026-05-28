# ADR-003: Low-cost chat backend (replace Rasa CALM)

## Status

Accepted

## Date

2026-05-28

## Context

FinGuard used Rasa CALM flows behind `POST /api/chat`, requiring **Rasa Pro** (`RASA_PRO_LICENSE`) for production-like behavior. Local development falls back to `mock-rasa.py`. CALM couples dialogue to a licensed runtime and multi-call LLM routing (via LiteLLM), while business logic already lives in Python actions and SQLite.

We need a **local-first, license-free** conversational backend with deterministic money flows and minimal LLM cost.

## Decision

Replace Rasa CALM with:

1. **Semantic Router** — local embedding-based intent classification (no LLM).
2. **Burr** — explicit FSM for multi-turn dialogue and pending confirmation.
3. **Instructor + Pydantic** — structured extraction only when slots cannot be filled by rules.
4. **Existing SQLite + services** — persistence and reports (refactored from `rasa-sdk` handlers).

**Deployment shape:**

- Single FastAPI app (`actions.server`) on port **5055**.
- `POST /webhooks/rest/webhook` — Rasa REST–compatible request/response for Next.js.
- `GET/PATCH/DELETE /data/*` — unchanged data API for the UI.
- Remove Docker `rasa/rasa-pro`, `backend/rasa/`, `mock-rasa.py`, and `rasa-sdk` dependency.

**Environment:** Prefer `CHAT_BACKEND_URL`; keep `RASA_URL` as a deprecated alias for one release.

## Alternatives considered

| Alternative | Rejected because |
|-------------|------------------|
| Keep Rasa Pro | License cost; CI secret dependency |
| Rasa OSS (DIET + stories) | High utterance maintenance; weaker multilingual routing than embeddings |
| Pure LLM agent with tools | Hard to enforce confirm-before-save; higher token cost |
| LangGraph | Heavier stack for a finite set of finance flows |
| Separate chat microservice on :5005 | Extra process/port; unified :5055 is simpler for local-first |

## Consequences

- **Positive:** No Pro license; CI runs without `RASA_PRO_LICENSE`; clearer ownership of dialogue in Python.
- **Positive:** LLM calls bounded to extraction steps.
- **Negative:** One-time cost to port flow YAML → Burr graph and utterance bank tuning.
- **Negative:** In-memory session state until optional SQLite `chat_sessions` table.
- **Supersedes:** [ADR-002: Rasa network trust](./002-rasa-network-trust.md) — same trust model applies to chat backend URL, not “Rasa” specifically.

## Verification

- All items in [archive/low-cost-migration/implementation-plan.md](../archive/low-cost-migration/implementation-plan.md) Section 12 (global verification).
- Golden webhook fixtures in `frontend/src/server/chat/fixtures/` pass without change.
