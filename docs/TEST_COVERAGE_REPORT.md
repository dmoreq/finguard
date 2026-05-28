# Test coverage report

**Last updated:** 2026-05-28
**Commands:** `make test-coverage` (or `uv run pytest tests/ --cov=actions` + `pnpm test:coverage`)

This report describes **what is tested**, **what is not**, and **recommended next steps**. It complements [TEST_STRATEGY.md](./TEST_STRATEGY.md).

---

## Executive summary

| Area | Tests | Line coverage | Verdict |
|------|-------|---------------|---------|
| **Backend** (`actions/`) | 63+ pytest | **~79%** | Strong for record/confirm; improved for reports after CP-2 tests |
| **Frontend** (Vitest, `.ts` only) | 67 | **~81%** | Strong on BFF/mappers; **React `.tsx` not in Vitest scope** |
| **E2E** (Playwright) | 7 specs | Not in % | Critical journeys locally; not in default CI |

Coverage percentages are useful but **understate UI risk**: Vitest only instruments `src/**/*.ts`, not components.

---

## How to reproduce

```bash
make test-coverage

# Or separately:
cd backend && uv run pytest tests/ -q --cov=actions --cov-report=term-missing
cd frontend && pnpm test:coverage
```

---

## Backend (~79% lines)

### Well covered

| Module | Notes |
|--------|--------|
| `factory.py`, `routing/composite.py`, `router.py` | Composition and facade |
| `session_store.py`, `webhook.py` | SQLite sessions + integration |
| `record_transaction.py` | Record → pending |
| `queries.py` | SQL layer |
| `routing/keyword.py`, `pending.py` | Intent + pending guard |

### Historically weak (addressed in CP-2 test batch)

| Module | Gap | Mitigation |
|--------|-----|------------|
| `get_balance.py` | Service unit tests | `test_services/test_reports.py` |
| `query_spending.py` | Service unit tests | Same |
| `list_transactions.py` | Service + webhook tests | Same + `test_webhook_reports.py` |

### Still under-covered

| Module | Cover (approx.) | Notes |
|--------|-----------------|--------|
| `extraction/gemini.py` | ~37% | Mocked only; no live Gemini in CI |
| `routing/semantic.py` | ~65% | Real embeddings; CI uses `ROUTER_MODE=keyword` |
| `delete_transaction.py` | ~56% | Discard — E2E exists |
| `dialogue/handlers/pending.py` | ~74% | Edit branches |
| `dialogue/collector.py` | ~68% | LLM error paths |

### Acceptable zero coverage

| File | Reason |
|------|--------|
| `chat/engine.py` | Re-export shim |
| `chat/extract/period.py` | Re-export to `extraction/period.py` |

---

## Frontend (~81% statements, TS only)

Vitest config: `include: ["src/**/*.ts"]` — **no `.tsx`**.

### Well covered

- `server/chat/*` — mappers, schemas, rate-limit (~99%)
- `app/api/data/*`, export routes (100%)
- `features/reports/finance-calculations.ts` (~97%)

### Gaps

| Area | Notes |
|------|--------|
| `lib/format.ts` | 0% — display helpers |
| `lib/data/financial-data.ts` | ~53% — fetch/hydration |
| All `.tsx` UI | Playwright only |
| `/api/chat` rate-limit branch | Partial |

Vitest thresholds: 70% lines/functions, 60% branches (currently passing).

---

## Critical paths

| ID | Journey | Unit/integration | E2E |
|----|---------|------------------|-----|
| CP-1 | Record → confirm | Strong | `confirm-transaction.spec.ts` |
| CP-2 | Balance / spending | **CP-2 tests added** | Partial |
| CP-3 | Discard pending | Medium | `discard-transaction.spec.ts` |
| CP-4 | Hydrate on load | Partial | Implicit |
| CP-5 | Settings profile | Strong | `settings-profile.spec.ts` |
| CP-6 | CSV export | Strong | `export-csv.spec.ts` |

---

## P1/P2 features

| Feature | Test approach |
|---------|----------------|
| Hybrid semantic router | Mocked; utterance bank runs in keyword mode in CI |
| Gemini extract | `test_extract_composite` (mocked) |
| SQLite sessions | `test_session_persist`, `test_chat_sessions` |

---

## Recommendations (remaining)

1. Optional CI job on pull requests for Playwright (currently nightly only).
2. Track coverage on PRs touching `actions/chat/` or `actions/services/`.
3. Include key `.tsx` in Vitest or expand E2E for income recording.

---

## Related docs

- [TEST_STRATEGY.md](./TEST_STRATEGY.md)
- [ROADMAP.md](./ROADMAP.md)
- [schemas/chat-payloads.json](./schemas/chat-payloads.json)
