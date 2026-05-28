# Test coverage report

**Last updated:** 2026-05-28
**Commands:** `make test-coverage` (or `uv run pytest tests/ --cov=actions` + `pnpm test:coverage`)

This report describes **what is tested**, **what is not**, and **recommended next steps**. It complements [TEST_STRATEGY.md](./TEST_STRATEGY.md).

---

## Executive summary

| Area | Tests | Line coverage | Verdict |
|------|-------|---------------|---------|
| **Backend** (`actions/`) | 108 pytest | **~87%** | Strong record/confirm/reports; delete service fully covered |
| **Frontend** (Vitest, `.ts` only) | 95 | **~93%** (`financial-data`, `format`) | Strong BFF/mappers; **React `.tsx` not in Vitest scope** |
| **E2E** (Playwright) | 10 specs | Not in % | CP-1/2/3 + income + balance chat; keyword router in CI webServer |

Coverage percentages are useful but **understate UI risk**: Vitest only instruments `src/**/*.ts`, not components.

---

## How to reproduce

```bash
make test-coverage

# Or separately:
cd backend && uv run pytest tests/ -q --cov=actions --cov-report=term-missing
cd frontend && pnpm test:coverage
make test-e2e
```

---

## Backend (~87% lines)

### Well covered

| Module | Notes |
|--------|--------|
| `factory.py`, `routing/composite.py`, `router.py` | Composition and facade |
| `session_store.py`, `webhook.py` | SQLite sessions + integration |
| `record_transaction.py`, `delete_transaction.py` | Record → pending; discard service |
| `queries.py` | SQL layer |
| `routing/keyword.py`, `pending.py` | Intent + pending guard |
| `extraction/period.py` | Period/category/trend hints (`test_extraction/test_period.py`) |
| `get_balance.py`, `query_spending.py`, `list_transactions.py` | CP-2 services + webhook integration |

### Still under-covered

| Module | Cover (approx.) | Notes |
|--------|-----------------|--------|
| `extraction/gemini.py` | ~37% | Mocked only; no live Gemini in CI |
| `routing/semantic.py` | ~65% | Real embeddings; CI/E2E use `ROUTER_MODE=keyword` |
| `dialogue/handlers/pending.py` | ~74% | Edit branches |
| `dialogue/collector.py` | ~68% | LLM error paths |
| `server.py` | ~70% | Backup restore edge paths |

### Acceptable zero coverage

| File | Reason |
|------|--------|
| `chat/engine.py` | Re-export shim |
| `chat/extract/period.py` | Re-export to `extraction/period.py` |

---

## Frontend (~93% statements, TS only)

Vitest config: `include: ["src/**/*.test.ts"]`, coverage on `src/**/*.ts` — **no `.tsx`**.

### Well covered

- `server/chat/*` — mappers, schemas, rate-limit (~99%)
- `app/api/data/*`, export routes, backup proxy (100%)
- `features/reports/finance-calculations.ts` (~93%)
- `lib/format.ts` (~95%) — **new** `format.test.ts`
- `lib/data/financial-data.ts` (~92%) — CRUD, backup, chat persistence tests expanded
- `/api/chat` — proxy, errors, **429 rate-limit branch**

### Gaps

| Area | Notes |
|------|--------|
| All `.tsx` UI | Playwright only |
| `features/auth/useSession.ts` | Trivial; excluded from coverage paths |

Vitest thresholds: 70% lines/functions, 60% branches (passing with headroom).

---

## Critical paths

| ID | Journey | Unit/integration | E2E |
|----|---------|------------------|-----|
| CP-1 | Record → confirm | Strong | `confirm-transaction.spec.ts` |
| CP-2 | Balance / spending | Strong | `balance-report.spec.ts` (dashboard + chat balance) |
| CP-3 | Discard pending | Medium | `discard-transaction.spec.ts` |
| CP-4 | Hydrate on load | Partial | Implicit |
| CP-5 | Settings profile | Strong | `settings-profile.spec.ts` |
| CP-6 | CSV export | Strong | `export-csv.spec.ts` |
| — | Record income | Service + router | `record-income.spec.ts` |

---

## E2E reliability notes

Playwright webServer (`scripts/playwright-webserver.sh`):

- Forces `ROUTER_MODE=keyword` (preserved over `backend/.env` hybrid default)
- Resets `backend/data/playwright-e2e.db` each run
- Restarts uvicorn so env/DB apply (does not reuse `make dev` backend)

---

## Recommendations (remaining)

1. Optional CI job on pull requests for Playwright (currently nightly only).
2. Track coverage on PRs touching `actions/chat/` or `actions/services/`.
3. Include key `.tsx` in Vitest or expand E2E for edit-pending flow.
4. API to reset chat session when clearing transactions (avoids stale pending state in long E2E runs).

---

## Related docs

- [TEST_STRATEGY.md](./TEST_STRATEGY.md)
- [ROADMAP.md](./ROADMAP.md)
- [schemas/chat-payloads.json](./schemas/chat-payloads.json)
