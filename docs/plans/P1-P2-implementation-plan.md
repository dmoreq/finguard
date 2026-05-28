# P1 + P2 implementation plan

**Status:** Implemented (2026-05-28)
**Audience:** Full-stack engineers
**Scope:** [ROADMAP](../ROADMAP.md) P1 (Semantic Router) and P2 (Gemini extraction + SQLite sessions)

**Principles (every step):**

| Principle | Application in this codebase |
|-----------|------------------------------|
| **DRY** | One `TransactionCollector`, one `CompositeIntentRouter`, one `ExtractResult` type — no duplicated collect/record paths |
| **SOLID — S** | `PendingConfirmationHandler`, `IntentDispatchHandler`, `SemanticIntentClassifier` each own one concern |
| **SOLID — O** | New routers/extractors implement `IntentClassifier` / `CompositeFieldExtractor` without editing handlers |
| **SOLID — L** | All `IntentClassifier` implementations honor the same `classify()` contract |
| **SOLID — I** | Small protocols in `routing/protocol.py`, `extraction/protocol.py`, `session_store.SessionStore` |
| **SOLID — D** | `DialogueEngine` and `webhook` depend on abstractions; `factory.py` is the composition root |
| **OOP** | Value objects (`TransactionDraft`, `IntentResult`); strategy objects for routing and extraction |

**Process:** TDD (RED → GREEN), one logical commit per step, pre-commit hooks must pass.

---

## 1. Goals and exit criteria

| Phase | Deliverable | Exit criteria | Status |
|-------|-------------|---------------|--------|
| **P1** | Hybrid semantic + keyword router | Pending guard; ≥85% keyword / ≥95% hybrid locally | Done |
| **P2a** | Rules-first + Gemini fallback | LLM only when rules incomplete; no DB on extract error | Done |
| **P2b** | SQLite `chat_sessions` | Pending survives restart | Done |

---

## 2. Package layout (post-refactor)

```text
chat/
  domain/          # Intent, ChatSession, TransactionDraft
  routing/         # pending, keyword, semantic, hybrid, composite
  extraction/      # rules, gemini, composite_extractor, schemas
  dialogue/        # DialogueEngine, handlers, collector
  settings.py      # env boundary (pydantic-settings)
  factory.py       # composition root
  session_store.py # SessionStore protocol + SqliteSessionStore
```

---

## 3. Step log (with design principles)

### Phase 0 — Baseline

| Step | Work | Principles |
|------|------|------------|
| 0.1 | Expand `utterances.jsonl` | **DRY:** single golden file for router eval |
| 0.2 | `test_utterance_bank_accuracy` + `CI_NO_SEMANTIC` | **S:** test only measures routing |

**Commit:** `test(backend): expand utterance bank for semantic router eval`

---

### P1 — Semantic Router

| Step | Work | Principles |
|------|------|------------|
| P1.1 | `CompositeIntentRouter` + `PendingIntentClassifier` | **S:** pending isolated; **D:** engine uses router facade only |
| P1.2 | `SemanticIntentClassifier` + `StubSemanticRouterBackend` | **O/L:** mock backend in tests; **I:** narrow `SemanticRouterBackend` protocol |
| P1.3 | `router_routes.yaml` + `load_route_definitions` | **DRY:** routes data separate from code |
| P1.4 | `HybridIntentClassifier` + `build_primary_classifier` | **O:** add mode without changing composite pending logic |
| P1.5 | `ChatSettings.ROUTER_MODE`; conftest forces `keyword` in CI | **D:** settings at boundary; **S:** config module one job |
| P1.6 | `factory.build_composite_router()` wired to engine | **D:** composition root owns wiring |
| P1.7 | Docs: runbook, `CI_NO_SEMANTIC`, TEST_STRATEGY | — |

**Commits:**

- `chore(backend): add semantic-router and gemini client dependencies`
- `feat(backend): add hybrid semantic router and chat settings`
- `docs: document semantic router setup and CI skip flag`

---

### P2 — Extraction + sessions

| Step | Work | Principles |
|------|------|------------|
| P2a | `ExtractResult` + `CompositeFieldExtractor` | **DRY:** one extract pipeline; **S:** rules vs LLM separated |
| P2b | `GeminiFieldExtractor` + Pydantic schema (`description` optional) | **S:** LLM at boundary; **O:** swap extractor via factory |
| P2c | `TransactionCollector` uses async `extract()` | **D:** collector depends on extractor abstraction |
| P2d | `.env.example`, runbook for `GEMINI_API_KEY` | — |
| P2e | `chat_sessions` table + queries | **S:** persistence separate from dialogue |
| P2f | `SqliteSessionStore` + `save_session` in webhook | **L:** `SessionStore` protocol; **D:** webhook persists after turn |
| P2g | `test_session_persist.py` | **Prove:** restart-safe pending flow |

**Commits:**

- `feat(backend): add rules-first gemini extraction pipeline`
- `feat(backend): persist chat sessions in sqlite`
- `test(backend): verify pending flow survives session reload`
- `docs: mark P1 P2 complete in roadmap and runbook`

---

## 4. Environment

See `backend/.env.example`:

```env
ROUTER_MODE=hybrid
SEMANTIC_ROUTER_THRESHOLD=0.72
LLM_EXTRACT_ENABLED=false
GEMINI_API_KEY=
```

Tests set `ROUTER_MODE=keyword` via `tests/conftest.py` to avoid downloading embeddings in CI.

---

## 5. Verification

```bash
cd backend && uv run pytest tests/ -q
cd frontend && pnpm test
make smoke   # optional
```

Local hybrid eval (downloads model once):

```bash
cd backend
ROUTER_MODE=hybrid uv run pytest tests/test_chat/test_router.py::test_utterance_bank_accuracy -q
```

---

## 6. Definition of done

- [x] Hybrid + pending guard implemented
- [x] Gemini extract optional, rules-first
- [x] SQLite sessions + integration test
- [x] 63 backend + 67 frontend tests pass
- [x] ROADMAP and ARCHITECTURE updated
- [ ] Optional: migrate to Outlines library (future)
- [ ] Burr (P3), DuckDB (P4) remain backlog
