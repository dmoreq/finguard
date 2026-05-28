# FinGuard — Product plan and next steps

**Author:** Product & engineering review
**Date:** 2026-05-28 (updated for Vietnamese-first)
**Status:** Active planning document
**Audience:** Founders, engineers, contributors

This report synthesizes [ROADMAP.md](./ROADMAP.md), [ARCHITECTURE.md](./ARCHITECTURE.md), [design/chat-backend-target.md](./design/chat-backend-target.md), [TEST_COVERAGE_REPORT.md](./TEST_COVERAGE_REPORT.md), ADRs, and the as-built codebase to answer: **what should FinGuard do next, and in what order?**

**Primary user assumption (2026-05-28):** The product owner uses **Vietnamese** for daily chat. English support remains useful for tests and future users, but **Vietnamese is the locale that must work first** — not an afterthought.

---

## Executive summary

FinGuard is a **local-first, chat-driven personal finance assistant** with a working MVP: record income/expenses in natural language, confirm pending transactions, view balance and spending reports, export CSV, and configure currency/timezone. The chat backend completed **P1 (semantic router)** and **P2 (Gemini extraction + SQLite sessions)**. **Phase 0 (stabilize)** is complete (86 backend tests, Playwright nightly CI, hybrid router eval).

**Critical gap:** The app is **English-first**. Keyword routing, rule extraction, bot templates, and UI copy assume English. A Vietnamese user cannot reliably complete the core loop today unless they code-switch to English or hybrid semantic routing happens to match a few samples (e.g. one phrase in `router_routes.yaml`).

**Recommendation:** Do **not** start Burr (P3), DuckDB (P4), or Phase 1 dashboard features until **Phase 0.5 (Vietnamese chat MVP)** is done. Chat in the user's language is the product — everything else is secondary.

**Priority order for the next 4–8 weeks:**

1. **Phase 0.5 — Vietnamese chat MVP** — routing, extraction, pending replies, bot copy, VND defaults.
2. **Phase 1 — Insight** — transaction list, manual CRUD, dashboard date ranges (templates in Vietnamese).
3. **Phase 2 — Budgets** — flagship PF feature, with Vietnamese utterances from day one.
4. **Phase 4+ — Auth / deploy** — only when leaving pure local-dev mode.

---

## Product vision (north star)

**One sentence:** Talk to your money — log transactions conversationally, confirm before anything is saved, and get clear summaries without spreadsheet work.

**Positioning today:** Hobby / personal tool — single local user, SQLite on disk, no cloud auth.
**Positioning target:** Trustworthy daily finance companion for **Vietnamese-speaking users first** — secure, sync’d, fast on mobile, deterministic on money actions.

**Non-negotiables** (from architecture ADRs — do not compromise):

| Principle | Implication |
|-----------|-------------|
| Deterministic money flows | No agent loops; confirm before write; templates for reports |
| LLM only when rules fail | Routing and reports stay zero-token where possible |
| Local-first option | Offline-capable path should remain viable |
| Explicit contracts | [chat-payloads.json](./schemas/chat-payloads.json) is the UI boundary |

**Locale strategy (decided):**

| Approach | Choice | Rationale |
|----------|--------|-----------|
| Primary locale | **Vietnamese (`vi`)** | Product owner and target daily use |
| Secondary locale | English (`en`) | Existing tests, docs, future users |
| Implementation | **Targeted templates + utterance bank** — not a full i18n framework yet | Ship fast; avoid over-engineering |
| Routing for Vietnamese | **Hybrid semantic router** + Vietnamese route samples | Keyword-only fails for non-English |
| Extraction for Vietnamese | **Rules for VND amounts/categories** + optional Gemini fallback | ADR-compliant; rules for `50k`, `1 triệu`, etc. |

---

## Current state assessment

### Shipped capabilities

| Area | What works | Evidence |
|------|------------|----------|
| **Chat: record** | Expense/income via NL → pending card → confirm/discard/edit | CP-1 E2E (English) |
| **Chat: reports** | Balance, spending by category, transaction list | CP-2 tests (English) |
| **Dashboard** | Monthly overview, category breakdown | `DashboardPanel` (English UI) |
| **Settings** | Currency (**VND** available), timezone | CP-5 E2E |
| **Export** | CSV download | CP-6 E2E |
| **Backend P1/P2** | Hybrid router, Gemini extract, SQLite sessions | [ROADMAP](./ROADMAP.md) |
| **Phase 0** | Webhook pending tests, LLM error tests, CI E2E + router eval | Complete 2026-05-28 |

### Language & locale gaps (blocking for Vietnamese users)

| Area | English today | Vietnamese gap |
|------|---------------|----------------|
| **Intent routing (keyword)** | `spent`, `balance`, `confirm`, … | No Vietnamese keywords |
| **Intent routing (semantic)** | ~40 English route samples | **1** Vietnamese sample (`chi tieu 50k an trua`) |
| **Utterance test bank** | 40 English cases | **0** Vietnamese cases in `utterances.jsonl` |
| **Pending replies** | `yes`, `confirm`, `discard`, `cancel` | No `xác nhận`, `hủy`, `đúng rồi`, … |
| **Edit parsing** | `change amount to 50` | No `sửa thành 50k`, `đổi danh mục`, … |
| **Amount rules** | `$`, `k`, `dollars` | Partial (`50k` works); no `triệu`, `nghìn`, `đ`, `500.000` |
| **Category rules** | `groceries`, `dining`, … | No `ăn uống`, `đi lại`, `chợ`, `cà phê`, `lương` |
| **Bot responses** | Hardcoded English strings in services | All user-facing replies English |
| **Welcome / UI** | English examples in chat | No Vietnamese prompts or button labels |
| **Profile defaults** | USD / UTC | Should default **VND / Asia/Ho_Chi_Minh** for local user |
| **Profile `locale`** | Not in schema | Needed to pick template language |

### Dialogue flows (6 today — Burr trigger is 7th)

| # | Flow | Intent(s) |
|---|------|-----------|
| 1 | Log expense | `log_expense` |
| 2 | Log income | `log_income` |
| 3 | Check balance | `check_balance` |
| 4 | Analyze spending | `analyze_spending` |
| 5 | List transactions | `list_transactions` |
| 6 | Manage pending | `manage_confirm`, `manage_discard`, `manage_edit` |

Adding **budgets**, **splits**, or **recurring transactions** as full multi-turn flows would likely hit the [Burr trigger](./ROADMAP.md#burr-backlog-detail). Plan those features together with a dialogue design review — **in Vietnamese and English utterance banks**.

### Explicitly not shipped (non-locale)

| Gap | Impact |
|-----|--------|
| **Authentication** | Blocks multi-user, sync, production |
| **Cloud sync / backup** | Data loss risk on one device |
| **Budgets / goals** | Core PF feature missing |
| **Recurring transactions** | Manual re-entry every period |
| **Transaction search/edit in UI** | Chat-only mutations after confirm |
| **PWA / mobile app** | Desktop-browser only |

### Engineering health

| Signal | Status |
|--------|--------|
| Backend tests | 86 passing |
| Phase 0 | Complete |
| Router accuracy (English, keyword) | 40/40 (100%) |
| Router accuracy (Vietnamese) | **Not measured** — no test bank |
| Playwright E2E | Nightly CI; English flows only |

**Verdict:** Strong English MVP foundation. **Primary product risk is language** — not missing budgets or backend instability. A Vietnamese user cannot depend on the app until Phase 0.5 ships.

---

## Strategic priorities (framework)

Use this order when evaluating any proposal:

```text
1. Correctness & trust     → money must never be wrong or silent-fail
2. Chat in user's language → Vietnamese routing, extraction, replies (Phase 0.5)
3. Core loop completion    → log → confirm → see impact (dashboard)
4. Control & insight       → budgets, trends, find/edit past entries
5. Reach & retention       → auth, sync, mobile/PWA
6. Platform scale          → DuckDB, Burr, Outlines, local LLM
```

**Rule:** Tier 6 items are **backlog until triggered** — see [ROADMAP.md](./ROADMAP.md).

**Rule:** Do not ship new chat intents (budgets, recurring) without **Vietnamese utterances in the same PR** as English.

---

## Recommended roadmap

### Phase 0 — Stabilize · **Complete (2026-05-28)**

| ID | Work | Status |
|----|------|--------|
| S-1 | Webhook tests discard / edit pending | Done — `test_webhook_pending.py` |
| S-2 | Gemini error-path tests | Done — `test_extract_llm.py` |
| S-3 | Playwright nightly CI | Done — `e2e-nightly.yml` |
| S-4 | Hybrid router eval CI | Done — `router-eval.yml` + `spike_router.py` |
| S-5 | English utterance bank (40 cases) | Done |

**Next:** Phase 2 (Budgets) — see [Phase 2](#phase-2--budgets-3-4-weeks--flagship-feature-after-locale).

---

### Phase 0.5 — Vietnamese chat MVP · **Complete (2026-05-28)**

Goal: A Vietnamese-speaking user can complete the **full core loop in Vietnamese** without code-switching to English.

| ID | Work | Status |
|----|------|--------|
| V-1–V-10 | Utterance bank, pending replies, VND parsing, templates, locale | **Done** |
| Golden flow | `test_webhook_vietnamese.py` | **Done** |
| CI | `router-eval-vi.yml` + `utterances-vi.jsonl` | **Done** |

**Next:** [Phase 1](#phase-1--insight-without-new-dialogue-complexity-2-3-weeks) (complete).

---

### Phase 1 — Insight without new dialogue complexity · **Complete (2026-05-28)**

**Prerequisite:** Phase 0.5 golden flow passes.

| ID | Feature | Status |
|----|---------|--------|
| F-1 | Trend comparison (chat + dashboard %) | **Done** |
| F-2 | Dashboard date range (tuần/tháng/tùy chọn) | **Done** |
| F-3 | Transaction list in UI | **Done** |
| F-4 | Manual transaction form (CRUD API + modal) | **Done** |
| F-5 | Category display labels (vi) | **Done** |
| F-6 | Data backup/restore | **Done** |

**Next:** [Phase 2 — Budgets](#phase-2--budgets-3-4-weeks--flagship-feature-after-locale).

---

### Phase 0.5 — Vietnamese chat MVP (1–2 weeks) · **Do first** _(archived plan)_

Goal: A Vietnamese-speaking user can complete the **full core loop in Vietnamese** without code-switching to English.

#### P0 — Must work for daily use

| ID | Work | Examples | Exit criteria |
|----|------|----------|---------------|
| V-1 | **Vietnamese utterance bank** | Per intent: 8–15 phrases in `utterances.jsonl` + `router_routes.yaml` | Hybrid accuracy ≥95% on Vietnamese subset |
| V-2 | **Vietnamese pending replies** | `xác nhận`, `đúng rồi`, `lưu`, `hủy`, `bỏ`, `không`, `sửa`, `đổi` | Pending handler tests in Vietnamese |
| V-3 | **Vietnamese amount parsing** | `50k`, `100 nghìn`, `1 triệu`, `500.000đ`, `50 ngàn`, `1tr` | Unit tests in `test_extract_rules.py` |
| V-4 | **Vietnamese category hints** | `ăn uống`, `đi lại`, `chợ`, `cà phê`, `lương`, `thưởng`, `tiền nhà` | Map to normalized slugs; display labels optional |
| V-5 | **Vietnamese edit phrases** | `sửa thành 60k`, `đổi danh mục thành ăn uống`, `sửa số tiền 80k` | Webhook edit tests in Vietnamese |
| V-6 | **Default profile for local user** | `VND`, `Asia/Ho_Chi_Minh` | Seed in `schema.py` / local user bootstrap |
| V-7 | **Hybrid router required for Vietnamese** | Document in runbook; CI keeps keyword for speed, add `utterances-vi.jsonl` eval job | Separate accuracy gate for Vietnamese |

#### P1 — Feels native (same phase or immediately after P0)

| ID | Work | Exit criteria |
|----|------|---------------|
| V-8 | **Vietnamese bot templates** | Record, confirm, discard, edit, balance, spending, errors — no hardcoded English in hot path for `vi` |
| V-9 | **Vietnamese welcome + chat examples** | `ChatWorkspace` welcome message and input placeholder |
| V-10 | **`locale` on profile** (optional field) | `vi` default; templates selected by locale; English fallback |

#### Vietnamese golden flow (acceptance test)

Manual or Playwright spec — **all steps in Vietnamese:**

| Step | User says | Expected |
|------|-----------|----------|
| 1 | *"Chi tiêu 80k cà phê sáng nay"* | Pending card, VND amount |
| 2 | *"Sửa thành 60k"* | Updated pending card |
| 3 | *"Xác nhận"* | Saved confirmation in Vietnamese |
| 4 | *"Tháng nay chi bao nhiêu?"* | Spending report |
| 5 | *"Số dư tháng này"* | Balance summary |

#### Implementation notes (architecture-aligned)

```text
Layer 1 — Add Vietnamese samples to semantic routes (zero tokens)
Layer 2 — Extend pending regex + keyword fallbacks for Vietnamese short replies
Layer 3 — VND amount + category rules; Gemini fallback for ambiguous Vietnamese text
Layer 4 — Locale-aware template strings (no LLM report prose)
```

**Do not:** Build a generic i18n framework, translate the entire UI, or route every Vietnamese turn through LLM.

**Defer to Phase 1 UI pass:** Dashboard labels, Settings page copy, Confirm/Discard button text (can stay English briefly if chat works).

---

### Phase 1 — Insight without new dialogue complexity (2–3 weeks) _(archived plan)_

**Prerequisite:** Phase 0.5 golden flow passes.

Goal: Increase daily usefulness using existing intents. **All new user-facing strings in Vietnamese first.**

| ID | Feature | Description | Effort |
|----|---------|-------------|--------|
| F-1 | **Trend comparison** | “Chi tiêu ăn uống tăng 12% so với tháng trước” | M |
| F-2 | **Dashboard date range** | Tuần / tháng / tùy chọn | M |
| F-3 | **Transaction list in UI** | Read-only table, filters | M |
| F-4 | **Manual transaction form** | Non-chat CRUD | M |
| F-5 | **Category display labels** | Slug → Vietnamese label in UI (`ăn uống`, …) | S |
| F-6 | **Data backup/restore** | Export/import bundle | S |

---

### Phase 2 — Budgets (3–4 weeks) · **Flagship feature (after locale)**

Goal: Answer *“Tháng này còn bao nhiêu cho ăn uống?”*

| ID | Capability | Vietnamese examples |
|----|------------|---------------------|
| B-1 | Monthly category budgets | *"Đặt ngân sách 2 triệu cho ăn uống tháng này"* |
| B-2 | Budget status in chat | *"Ăn uống còn bao nhiêu?"* |
| B-3 | Budget bars in dashboard | Visual progress |
| B-4 | Soft alerts | Template when crossing 80%/100% |

**Engineering note:** Likely the **7th dialogue flow** → evaluate Burr when multi-turn budget setup is needed.

---

### Phase 3 — Recurring & automation (2–3 weeks)

| ID | Feature | Vietnamese example |
|----|---------|---------------------|
| R-1 | Recurring templates | *"Tiền nhà 5 triệu mỗi tháng"* |
| R-2 | Apply due recurring | Confirm batch in chat |
| R-3 | Optional auto-confirm | Off by default |

---

### Phase 4 — Real users & deploy (4–6 weeks)

Unchanged from prior plan — auth, Postgres, RLS, hosted deploy. See [production-deploy.md](./runbooks/production-deploy.md).

---

### Phase 5 — Platform backlog (trigger-driven)

| Item | Trigger |
|------|---------|
| **Burr (P3)** | 7th flow, brittle handlers |
| **DuckDB (P4)** | Slow analytics |
| **Full i18n framework** | Second locale beyond vi/en with shared UI |
| **Outlines / local LLM** | Per [ROADMAP](./ROADMAP.md) |

---

## Feature backlog (prioritized)

| Rank | Feature | User value | Effort | Phase |
|------|---------|------------|--------|-------|
| **1** | **Vietnamese chat MVP (V-1–V-10)** | **Core product for PO** | **M** | **0.5** |
| 2 | Transaction list + manual CRUD (F-3, F-4) | Control | M | 1 |
| 3 | Dashboard date ranges (F-2) | Insight | M | 1 |
| 4 | Category Vietnamese labels (F-5) | UX | S | 1 |
| 5 | **Budgets (B-1–B-4)** | Differentiation | L | 2 |
| 6 | Trend comparison (F-1) | Insight | M | 1 |
| 7 | Recurring (R-1–R-3) | Convenience | L | 3 |
| 8 | Backup/restore (F-6) | Safety | S | 1 |
| 9 | Auth + Postgres | Scale | XL | 4 |
| 10 | English UI parity | Future users | M | 1–2 |
| 11 | Burr / DuckDB | Engineering | L | 5 |

**Effort key:** S = days, M = 1–2 weeks, L = 2–4 weeks, XL = 1+ month.

---

## What not to build (yet)

- Full react-i18n / next-intl for every string before chat works in Vietnamese
- LLM for every Vietnamese routing decision (use semantic routes + rules)
- LangGraph / tool-calling agents for money flows
- LLM-generated report prose
- Budgets in English only
- Production multi-user on exposed SQLite

---

## Decisions (product owner)

| # | Question | Decision |
|---|----------|----------|
| D-1 | Primary language for next 3 months? | **Vietnamese** |
| D-2 | Secondary language? | English (tests + docs) |
| D-3 | Default currency / timezone? | **VND / Asia/Ho_Chi_Minh** |
| D-4 | First feature after Phase 0.5? | Phase 1 insight (not budgets before chat works) |
| D-5 | i18n approach? | Template maps per locale — not framework-first |
| D-6 | Router mode for Vietnamese dev? | **Hybrid** locally; separate `utterances-vi.jsonl` CI eval |
| D-7 | Enable `LLM_EXTRACT_ENABLED` for Vietnamese gaps? | Yes for beta, rules-first; log when invoked |
| D-8 | Chat history sync with auth? | Defer to Phase 4; device-local until then |

---

## Success metrics

### Phase 0.5 (Vietnamese)

| Metric | Target |
|--------|--------|
| Golden flow (5 steps, Vietnamese) | 100% pass manual or E2E |
| Router accuracy (`utterances-vi.jsonl`, hybrid) | ≥95% |
| Pending confirm/discard/edit in Vietnamese | Webhook tests green |
| VND amount parsing cases | 100% on unit fixture list |
| Bot replies for `locale=vi` | No English in confirm/discard/save path |

### Phase 1–2 (ongoing)

| Metric | Target |
|--------|--------|
| Record → confirm completion (Vietnamese) | ≥90% in user testing |
| Time to first confirmed transaction | <2 minutes |
| Budget queries (when shipped) | Vietnamese fixtures 100% |

### Engineering

| Metric | Target |
|--------|--------|
| Backend + frontend tests | Green on every PR |
| Playwright critical paths | Pass (add Vietnamese spec in Phase 0.5) |
| English router bank | ≥85% keyword / ≥95% hybrid (unchanged) |

---

## Suggested sprint plan (next 6 weeks)

### Sprint 1 (week 1–2): Vietnamese chat MVP (Phase 0.5)

- V-1 Vietnamese utterance bank + router routes
- V-2 Pending replies (confirm / discard / edit)
- V-3–V-5 Amount, category, edit parsing
- V-6 VND + Ho Chi Minh defaults
- V-8–V-9 Vietnamese templates + welcome message
- **Deliverable:** Golden flow passes entirely in Vietnamese

### Sprint 2 (week 3–4): Polish + Phase 1 start

- V-10 `locale` on profile (if not done in Sprint 1)
- Playwright spec for Vietnamese golden flow
- F-3 Transaction list UI (Vietnamese labels)
- F-5 Category display names
- **Deliverable:** Daily use comfortable in Vietnamese

### Sprint 3 (week 5–6): Insight + budgets prep

- F-2 Dashboard date range
- F-4 Manual transaction form
- B-1 budget schema design + Vietnamese utterances drafted
- **Deliverable:** Control surfaces without English chat fallback

---

## Documentation map

| Topic | Document |
|-------|----------|
| As-built architecture | [ARCHITECTURE.md](./ARCHITECTURE.md) |
| Engineering backlog | [ROADMAP.md](./ROADMAP.md) |
| Target chat design | [design/chat-backend-target.md](./design/chat-backend-target.md) |
| Test strategy | [TEST_STRATEGY.md](./TEST_STRATEGY.md) |
| Local dev / router eval | [runbooks/local-development.md](./runbooks/local-development.md) |
| **This plan** | PRODUCT_PLAN.md |
| **Use case inventory** | [USE_CASE_CATALOG.md](./USE_CASE_CATALOG.md) |
| **Feature specs (RFCs)** | [specs/README.md](./specs/README.md) |

---

## Appendix A — Vietnamese utterance seeds (Phase 0.5)

Use as starting points for `utterances-vi.jsonl` and `router_routes.yaml`:

| Intent | Example utterances |
|--------|-------------------|
| `log_expense` | *Chi tiêu 50k ăn trưa* · *Mua cà phê 35k* · *Trả 200k tiền điện* · *Hôm nay tiêu 80k Grab* |
| `log_income` | *Nhận lương 15 triệu* · *Freelance 3 triệu* · *Thưởng 2 triệu* |
| `check_balance` | *Số dư tháng này* · *Thu chi tháng này thế nào* · *Còn bao nhiêu tiền* |
| `analyze_spending` | *Tháng nay chi bao nhiêu* · *Chi tiêu theo danh mục* · *Tuần này tiêu gì nhiều nhất* |
| `list_transactions` | *Xem giao dịch gần đây* · *Lịch sử chi tiêu* |
| `manage_confirm` | *Xác nhận* · *Đúng rồi* · *Lưu* · *Ok* |
| `manage_discard` | *Hủy* · *Bỏ* · *Không lưu* · *Xóa* |
| `manage_edit` | *Sửa thành 60k* · *Đổi danh mục thành ăn uống* · *Sửa số tiền 100k* |

---

## Appendix B — Amount & category patterns (Vietnamese)

| Pattern | Meaning | Normalized |
|---------|---------|------------|
| `50k`, `50K` | 50,000 VND | `50000` |
| `1 triệu`, `1tr`, `1 tr` | 1,000,000 | `1000000` |
| `500.000đ`, `500000 vnd` | 500,000 VND | `500000` |
| `100 nghìn`, `100 ngàn` | 100,000 | `100000` |

| Vietnamese term | Suggested slug |
|-----------------|----------------|
| ăn uống, ăn trưa, cà phê | `an-uong` or map to `dining` |
| đi lại, grab, xăng | `di-lai` / `transport` |
| chợ, đi chợ | `groceries` |
| lương, tiền lương | `salary` |
| tiền nhà, thuê nhà | `rent` |

Pick one slug strategy (Vietnamese slugs vs English slugs with vi display labels) in Phase 0.5 and document in an ADR or runbook note.

---

## Appendix C — Risk register

| Risk | Likelihood | Impact | Mitigation |
|------|------------|--------|------------|
| **Vietnamese routing fails in keyword CI** | High | Medium | Separate `utterances-vi.jsonl` + hybrid eval job |
| Keyword-only dev misleads Vietnamese testing | Medium | High | Runbook: use `ROUTER_MODE=hybrid` for vi |
| Mixed slugs (vi/en categories) | Medium | Medium | ADR on slug strategy; display layer for labels |
| Over-reliance on Gemini for Vietnamese | Medium | Medium | Rules-first; utterance bank tracks rule coverage |
| Handler sprawl without Burr | Medium | High | Burr spike before multi-turn budget wizard |
| English-only E2E misses locale regressions | Medium | High | Vietnamese Playwright spec in Phase 0.5 |

---

## Revision history

| Date | Change |
|------|--------|
| 2026-05-28 | Initial product plan |
| 2026-05-28 | Phase 0 marked complete; Vietnamese-first locale; Phase 0.5 added; priorities reordered |
