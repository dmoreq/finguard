# FinGuard — Use case & functionality catalog

**Author:** Product owner review
**Date:** 2026-05-28
**Status:** Living reference
**Related:** [PRODUCT_PLAN.md](./PRODUCT_PLAN.md) · [ROADMAP.md](./ROADMAP.md) · [ARCHITECTURE.md](./ARCHITECTURE.md)

This document lists **user-facing use cases** a personal finance chat assistant may need, maps each to **implementation status**, and notes **Vietnamese readiness** where relevant. It is the companion to the prioritization plan in [PRODUCT_PLAN.md](./PRODUCT_PLAN.md).

---

## How to read this catalog

### Status legend

| Status | Meaning |
|--------|---------|
| **Implemented** | Shipped; usable today (see locale notes) |
| **Partial** | Core exists but gaps limit daily use |
| **Planned** | Named in [PRODUCT_PLAN.md](./PRODUCT_PLAN.md) with phase ID |
| **Roadmap** | Engineering backlog in [ROADMAP.md](./ROADMAP.md); not scheduled as product work |
| **Future** | Valid user need; not yet in product or engineering plans |
| **Out of scope** | Explicit non-goal per ADR / ROADMAP |

### Locale column (Vietnamese)

| Symbol | Meaning |
|--------|---------|
| **VI ✅** | Works reliably in Vietnamese today |
| **VI 🟡** | Partial (e.g. amounts like `50k` work; full phrases do not) |
| **VI ❌** | English-first; Vietnamese user must code-switch or hit unknown intent |

**Default profile today:** USD, UTC, English UI — not ideal for a Vietnamese primary user ([PRODUCT_PLAN Phase 0.5](./PRODUCT_PLAN.md#phase-05--vietnamese-chat-mvp-12-weeks--do-first)).

### Priority (MoSCoW)

| Tag | Meaning |
|-----|---------|
| **Must** | Required for daily personal finance use |
| **Should** | Expected in a competitive PF app within 3–6 months |
| **Could** | Nice-to-have / power user |
| **Won't (now)** | Deferred or explicitly out of scope |

---

## Executive summary

| Category | Implemented | Partial | Planned | Future / Roadmap |
|----------|-------------|---------|---------|------------------|
| Record transactions (chat) | 4 | 3 | 1 | 2 |
| Manage pending / confirmed | 5 | 2 | 2 | 1 |
| Reports & queries (chat) | 3 | 2 | 1 | 2 |
| Dashboard & charts | 3 | 2 | 2 | 1 |
| Settings & profile | 3 | 2 | 1 | 1 |
| Data export & hygiene | 3 | 1 | 1 | 1 |
| Language & locale (VI) | 0 | 2 | 10 | 1 |
| Auth, sync, deploy | 0 | 1 | 6 | 2 |
| Budgets & goals | 0 | 0 | 4 | 2 |
| Recurring & automation | 0 | 0 | 3 | 1 |
| Mobile & platform | 0 | 1 | 0 | 4 |
| Engineering platform | 2 | 0 | 0 | 4 |

**Headline:** FinGuard delivers a **solid English MVP** for chat-based logging, confirm-before-save, basic reports, dashboard, CSV export, and local settings. For a **Vietnamese primary user**, most chat use cases are **Partial or not implemented** until Phase 0.5. **Budgets, recurring, auth, and mobile** are largely **Planned** or **Future**.

---

## 1. Transaction capture (chat)

Natural-language entry is the core product loop.

| ID | Use case | User story | Status | Phase / ref | VI | Priority |
|----|----------|------------|--------|-------------|-----|----------|
| TC-01 | Log expense in one message | *"Spent $45 on groceries"* → pending card | **Implemented** | `log_expense`, `record_transaction` | VI ❌ | Must |
| TC-02 | Log income in one message | *"Got paid $3,000 salary"* → pending card | **Implemented** | `log_income` | VI ❌ | Must |
| TC-03 | Log expense with amount + category only | *"Coffee 4.50 dining"* | **Implemented** | Rule extraction | VI 🟡 (`50k` works) | Must |
| TC-04 | Multi-turn slot fill (missing amount) | Bot asks for amount, then records | **Implemented** | `TransactionCollector`, `collecting` phase | VI ❌ | Should |
| TC-05 | Multi-turn slot fill (missing category) | Bot asks for category | **Implemented** | Same | VI ❌ | Should |
| TC-06 | Optional description / memo | Free text on transaction | **Partial** | Schema + Gemini optional; weak rule extract | VI ❌ | Could |
| TC-07 | Relative dates in chat | *"yesterday"*, *"today"* | **Partial** | `parse_relative_date`; English-centric | VI ❌ | Should |
| TC-08 | LLM fallback when rules fail | Ambiguous message still parsed | **Partial** | `LLM_EXTRACT_ENABLED` off by default | VI 🟡 (if enabled) | Should |
| TC-09 | Vietnamese expense phrases | *"Chi tiêu 80k cà phê"* | **Planned** | Phase **0.5** V-1, V-3, V-4 | VI ❌ → Planned | Must |
| TC-10 | Vietnamese income phrases | *"Nhận lương 15 triệu"* | **Planned** | Phase **0.5** | VI ❌ → Planned | Must |
| TC-11 | VND amount formats | `50k`, `1 triệu`, `500.000đ` | **Planned** | Phase **0.5** V-3 | VI 🟡 → Planned | Must |
| TC-12 | Receipt / photo capture | Photo → OCR → pending | **Future** | Mobile / OCR not planned | VI ❌ | Could |
| TC-13 | Voice input | Speak transaction | **Future** | — | — | Could |
| TC-14 | Bulk import (CSV/bank) | Import statement file | **Future** | Export only today | — | Could |

**Evidence:** `backend/actions/chat/dialogue/collector.py`, `record_transaction.py`, E2E `confirm-transaction.spec.ts`.

---

## 2. Pending transaction management (confirm / edit / discard)

Confirm-before-save is a product differentiator and ADR requirement.

| ID | Use case | User story | Status | Phase / ref | VI | Priority |
|----|----------|------------|--------|-------------|-----|----------|
| PM-01 | Review pending card in chat | See amount, category, date before save | **Implemented** | `transaction_pending` payload, `TransactionCard` | VI ✅ UI | Must |
| PM-02 | Confirm via chat | *"confirm"* / *"yes"* | **Implemented** | `manage_confirm`, CP-1 E2E | VI ❌ | Must |
| PM-03 | Confirm via UI button | Click Confirm on card | **Implemented** | Sends structured confirm to backend | VI ✅ UI | Must |
| PM-04 | Discard via chat | *"discard"* / *"cancel"* | **Implemented** | `manage_discard`, E2E | VI ❌ | Must |
| PM-05 | Discard via UI button | Click Discard | **Implemented** | E2E `discard-transaction.spec.ts` | VI ✅ UI | Must |
| PM-06 | Edit amount via chat | *"change amount to 50"* | **Implemented** | Phase 0 webhook tests | VI ❌ | Must |
| PM-07 | Edit category via chat | *"change category to dining"* | **Implemented** | Phase 0 webhook tests | VI ❌ | Must |
| PM-08 | Edit via card UI (inline) | Edit fields on card before confirm | **Partial** | Card has edit mode; confirm sends English structured message | VI 🟡 | Should |
| PM-09 | Edit description / date via chat | *"change date to yesterday"* | **Partial** | Description edit rules exist; date edit limited | VI ❌ | Could |
| PM-10 | Vietnamese confirm / discard / edit | *"Xác nhận"*, *"Hủy"*, *"Sửa thành 60k"* | **Planned** | Phase **0.5** V-2, V-5 | VI ❌ → Planned | Must |
| PM-11 | Pending survives backend restart | Session restored from SQLite | **Implemented** | `chat_sessions`, `test_session_persist.py` | — | Must |
| PM-12 | Only one pending at a time | Clear behavior if new expense while pending | **Partial** | Implicit; not heavily tested | — | Should |
| PM-13 | Idempotent confirm | Confirm twice does not double-save | **Implemented** | `update_transaction` confirmed guard | — | Must |

---

## 3. Confirmed transaction management

After save, users need control over historical data.

| ID | Use case | User story | Status | Phase / ref | VI | Priority |
|----|----------|------------|--------|-------------|-----|----------|
| CM-01 | List confirmed transactions (chat) | *"Show recent transactions"* | **Implemented** | `list_transactions` intent | VI ❌ | Should |
| CM-02 | List with period filter (chat) | *"last 7 days"*, *"this month"* | **Partial** | English period patterns only | VI ❌ | Should |
| CM-03 | List with category filter (chat) | *"grocery spending"* | **Partial** | English category hints | VI ❌ | Could |
| CM-04 | View transaction list in UI | Dedicated table / page | **Planned** | Phase **1** F-3 | — | Should |
| CM-05 | Edit confirmed transaction (UI) | Fix mistake after confirm | **Planned** | Phase **1** F-4 | — | Should |
| CM-06 | Edit confirmed transaction (chat) | *"Change yesterday's coffee to $5"* | **Future** | No intent | VI ❌ | Could |
| CM-07 | Delete single confirmed transaction | Remove one row | **Future** | Only discard pending + clear all | — | Should |
| CM-08 | Delete all transactions | Reset data | **Implemented** | Header "Clear txs", `DELETE /data/transactions` | VI ✅ UI | Could |
| CM-09 | Soft-delete / audit trail | See discarded history | **Partial** | `discarded` status in DB; hidden from list API | — | Could |

---

## 4. Reports & financial queries (chat)

Template-based SQL reports (no LLM prose per ADR).

| ID | Use case | User story | Status | Phase / ref | VI | Priority |
|----|----------|------------|--------|-------------|-----|----------|
| RQ-01 | Balance / net (income − expenses) | *"What's my balance this month?"* | **Implemented** | `check_balance`, `balance` payload | VI ❌ | Must |
| RQ-02 | Spending total by period | *"How much did I spend last month?"* | **Implemented** | `analyze_spending` | VI ❌ | Must |
| RQ-03 | Spending by category | Breakdown in report card | **Implemented** | `spending_report` payload | VI ❌ | Must |
| RQ-04 | Category-scoped spending query | *"Show my grocery spending"* | **Partial** | `parse_category_hint` English only | VI ❌ | Should |
| RQ-05 | Period: this month / last month | Default reporting windows | **Implemented** | `parse_period_from_text` | VI ❌ | Must |
| RQ-06 | Period: last 7d / 30d / 3m / YTD | Extended windows | **Partial** | English regex only | VI ❌ | Should |
| RQ-07 | Vietnamese report questions | *"Tháng nay chi bao nhiêu?"*, *"Số dư tháng này"* | **Planned** | Phase **0.5** V-1, V-8 | VI ❌ → Planned | Must |
| RQ-08 | Trend vs prior period | *"12% more on dining vs last month"* | **Planned** | Phase **1** F-1 | VI ❌ | Should |
| RQ-09 | Income-only or expense-only summary | Tab-style breakdown | **Partial** | Dashboard tabs; chat is combined balance/spend | — | Could |
| RQ-10 | Custom date range in chat | *"From Jan 1 to Jan 15"* | **Future** | — | VI ❌ | Could |
| RQ-11 | LLM-generated narrative report | Prose summary of finances | **Out of scope** | [ROADMAP non-goals](./ROADMAP.md) | — | Won't |
| RQ-12 | Fast analytics at scale | Large history aggregations | **Roadmap** | DuckDB P4 when slow | — | Won't (now) |

**Evidence:** `get_balance.py`, `query_spending.py`, `test_webhook_reports.py`.

---

## 5. Dashboard & visualization (UI)

Sidebar overview driven by confirmed transactions.

| ID | Use case | User story | Status | Phase / ref | VI | Priority |
|----|----------|------------|--------|-------------|-----|----------|
| DB-01 | Monthly overview (net, income, expenses) | Glance at current month | **Implemented** | `DashboardPanel`, `finance-calculations` | VI ❌ labels | Must |
| DB-02 | Category breakdown chart | See where money goes | **Implemented** | SVG bars in dashboard | VI ❌ | Must |
| DB-03 | Income / expense / overview tabs | Switch views | **Implemented** | Tab UI | VI ❌ | Should |
| DB-04 | Toggle dashboard visibility | Show / hide overview | **Implemented** | Header button | VI ✅ | Could |
| DB-05 | Dashboard respects timezone | Month boundaries correct | **Partial** | Profile timezone used in backend; dashboard uses client month | VI 🟡 | Should |
| DB-06 | Dashboard date range picker | Not only current month | **Planned** | Phase **1** F-2 | — | Should |
| DB-07 | VND / profile currency in charts | Format with user currency | **Partial** | Profile currency in reports; `formatMoney` hardcodes USD in UI | VI 🟡 | Must |
| DB-08 | Vietnamese category labels | *Ăn uống* not `dining` | **Planned** | Phase **1** F-5 | VI ❌ → Planned | Should |
| DB-09 | Budget progress bars | Category vs limit | **Planned** | Phase **2** B-3 | VI ❌ | Should |
| DB-10 | Export chart / share report | PDF or image | **Future** | — | — | Could |

---

## 6. Settings & profile

| ID | Use case | User story | Status | Phase / ref | VI | Priority |
|----|----------|------------|--------|-------------|-----|----------|
| ST-01 | Set display name | Personalize profile | **Implemented** | Settings page, `PATCH /data/profile` | VI ✅ | Could |
| ST-02 | Set currency | VND, USD, … | **Implemented** | VND in list; default USD | VI 🟡 | Must |
| ST-03 | Set timezone | Asia/Ho_Chi_Minh, … | **Implemented** | E2E settings | VI 🟡 | Must |
| ST-04 | Default VND + Ho Chi Minh for local user | Sensible out-of-box defaults | **Planned** | Phase **0.5** V-6 | VI ❌ → Planned | Must |
| ST-05 | Language / locale preference | UI + bot in Vietnamese | **Planned** | Phase **0.5** V-10 | VI ❌ → Planned | Must |
| ST-06 | Enable / disable LLM extraction | Privacy / cost control | **Partial** | Backend env only; no Settings UI | — | Could |
| ST-07 | Notification preferences | Alerts, reminders | **Future** | — | — | Could |
| ST-08 | Custom category taxonomy | Manage category list | **Future** | Fixed lists in UI types; free slug in DB | — | Should |

---

## 7. Data storage, export & hygiene

| ID | Use case | User story | Status | Phase / ref | VI | Priority |
|----|----------|------------|--------|-------------|-----|----------|
| DS-01 | Persist transactions locally | SQLite on disk | **Implemented** | `backend/data/finguard.db` | — | Must |
| DS-02 | Persist chat history in browser | Reload chat on refresh | **Implemented** | localStorage via `chat-storage` | — | Should |
| DS-03 | Hydrate transactions on load | Sidebar + chat sync | **Implemented** | CP-4 partial | — | Must |
| DS-04 | Export transactions CSV | Download for Excel | **Implemented** | `/api/transactions/export`, E2E | VI ✅ | Should |
| DS-05 | Clear chat history only | Keep transactions | **Implemented** | Header "Clear chat" | VI ✅ | Could |
| DS-06 | Backup / restore full database | Move to new device | **Planned** | Phase **1** F-6 | — | Should |
| DS-07 | Cloud sync across devices | Same data on phone + laptop | **Planned** | Phase **4** auth + Postgres | — | Should |
| DS-08 | Encrypted backup | Secure export | **Future** | — | — | Could |
| DS-09 | GDPR-style delete account | Erase all user data | **Future** | Single local user today | — | Future |

---

## 8. Chat UX & assistant behavior

| ID | Use case | User story | Status | Phase / ref | VI | Priority |
|----|----------|------------|--------|-------------|-----|----------|
| UX-01 | Welcome message + examples | Onboarding in chat | **Implemented** | English welcome | VI ❌ | Must |
| UX-02 | Vietnamese welcome + examples | Localized onboarding | **Planned** | Phase **0.5** V-9 | VI ❌ → Planned | Must |
| UX-03 | Typing indicator | Feedback while waiting | **Implemented** | `TypingIndicator` | — | Could |
| UX-04 | Error message + retry | Backend down / timeout | **Partial** | Error bubble + retry; E2E `error-rasa-down` | VI ❌ | Should |
| UX-05 | Rate limit friendly message | Too many messages | **Implemented** | `/api/chat` 429 | VI ❌ | Should |
| UX-06 | Chitchat / help | *"hello"*, *"help"* | **Partial** | English help text only | VI ❌ | Could |
| UX-07 | Unknown intent guidance | Clarify what app can do | **Implemented** | English fallback | VI ❌ | Should |
| UX-08 | Markdown in messages | Bold, lists in replies | **Implemented** | `markdown.tsx` | — | Could |
| UX-09 | Safe markdown (no XSS) | HTML escaped | **Implemented** | Per hobby backlog | — | Must |
| UX-10 | Accessibility smoke | Basic a11y | **Partial** | `a11y-smoke.spec.ts` | — | Should |

---

## 9. Language & localization (Vietnamese-first)

Cross-cutting capabilities referenced throughout this catalog.

| ID | Use case | Status | Phase / ref | Priority |
|----|----------|--------|-------------|----------|
| L-01 | Vietnamese intent routing | **Planned** | **0.5** V-1, V-7 | Must |
| L-02 | Vietnamese pending replies | **Planned** | **0.5** V-2 | Must |
| L-03 | Vietnamese amount parsing | **Planned** | **0.5** V-3 | Must |
| L-04 | Vietnamese category mapping | **Planned** | **0.5** V-4 | Must |
| L-05 | Vietnamese edit phrases | **Planned** | **0.5** V-5 | Must |
| L-06 | Vietnamese bot templates | **Planned** | **0.5** V-8 | Must |
| L-07 | Vietnamese UI (dashboard, settings, buttons) | **Planned** | **0.5** V-9; Phase **1** F-5 | Should |
| L-08 | `locale` field on profile | **Planned** | **0.5** V-10 | Should |
| L-09 | Vietnamese E2E golden flow | **Planned** | Sprint 2 in PRODUCT_PLAN | Must |
| L-10 | English parity maintained | **Partial** | Tests + utterance bank | Should |
| L-11 | Full i18n framework (next-intl, etc.) | **Future** | Phase **5** mention | Won't (now) |

---

## 10. Budgets, goals & spending control

| ID | Use case | User story | Status | Phase / ref | VI | Priority |
|----|----------|------------|--------|-------------|-----|----------|
| BG-01 | Set monthly category budget (chat) | *"Budget 2M for food this month"* | **Planned** | Phase **2** B-1 | VI ❌ | Should |
| BG-02 | Check budget status (chat) | *"How much left for dining?"* | **Planned** | Phase **2** B-2 | VI ❌ | Should |
| BG-03 | Budget bars on dashboard | Visual progress | **Planned** | Phase **2** B-3 | VI ❌ | Should |
| BG-04 | Alert at 80% / 100% of budget | On confirm or query | **Planned** | Phase **2** B-4 | VI ❌ | Could |
| BG-05 | Savings goals | *"Save 10M for trip"* | **Future** | — | VI ❌ | Could |
| BG-06 | Rollover unused budget | Month to month | **Future** | — | — | Could |

**Engineering note:** Budgets likely trigger **7th dialogue flow** → [Burr P3](./ROADMAP.md#burr-backlog-detail) evaluation.

---

## 11. Recurring & scheduled transactions

| ID | Use case | User story | Status | Phase / ref | VI | Priority |
|----|----------|------------|--------|-------------|-----|----------|
| RC-01 | Define recurring expense/income | Rent, salary monthly | **Planned** | Phase **3** R-1 | VI ❌ | Should |
| RC-02 | Apply due items (confirm batch) | *"Apply recurring for this month"* | **Planned** | Phase **3** R-2 | VI ❌ | Should |
| RC-03 | Auto-confirm recurring (opt-in) | Skip manual confirm | **Planned** | Phase **3** R-3 | — | Could |
| RC-04 | Remind user when recurring due | Push / email | **Future** | Needs notifications | — | Could |

---

## 12. Authentication, multi-user & deployment

| ID | Use case | User story | Status | Phase / ref | Priority |
|----|----------|--------|-------------|----------|
| AU-01 | Login / signup | Secure access | **Partial** | `/login` redirects to chat; no auth | Phase **4** | Should |
| AU-02 | Multi-user data isolation | Each user sees own data | **Future** | Single `LOCAL_USER_ID` | Phase **4** U-3 | Must (hosted) |
| AU-03 | Hosted production deploy | Vercel + backend VPS | **Partial** | Draft [runbook](./runbooks/production-deploy.md) | Phase **4** | Should |
| AU-04 | Postgres instead of SQLite | Multi-user OLTP | **Planned** | Phase **4** U-2 | Must (hosted) |
| AU-05 | Service-role / RLS patterns | Supabase archive | **Future** | [archive/supabase](./archive/supabase/) | Phase **4** | Must (hosted) |
| AU-06 | Forgot password | Account recovery | **Future** | Mentioned in archived tracker only | Could |
| AU-07 | Private backend network | Webhook not public | **Planned** | Phase **4** U-5, ADR-003 | Must (hosted) |
| AU-08 | Distributed rate limiting | Redis / Upstash | **Planned** | Phase **4** U-4 | Should (scale) |

---

## 13. Mobile, PWA & notifications

| ID | Use case | User story | Status | Phase / ref | Priority |
|----|----------|--------|-------------|----------|
| MB-01 | Install as PWA | Add to home screen | **Future** | [archive prototype options](./archive/prototype-to-product-options.md) | Could |
| MB-02 | Native iOS / Android app | Expo / React Native | **Future** | Phase **5** / archive | Could |
| MB-03 | Push notification (budget alert) | Mobile alert | **Future** | — | Could |
| MB-04 | Offline chat queue | Record without network | **Future** | Local-first partial | Could |
| MB-05 | Responsive mobile web | Usable on phone browser | **Partial** | Not primary design target | Should |

---

## 14. Integrations & advanced features

| ID | Use case | User story | Status | Phase / ref | Priority |
|----|----------|--------|-------------|----------|
| IN-01 | Bank feed / open banking | Auto-import transactions | **Future** | — | Could |
| IN-02 | Split transaction | Shared bill with friends | **Future** | PRODUCT_PLAN rank 10 | Could |
| IN-03 | Multi-currency transactions | USD expense, VND account | **Future** | Single profile currency | Could |
| IN-04 | Tags / labels beyond category | `#vacation` | **Future** | — | Could |
| IN-05 | Search full-text history | Find *"starbucks"* | **Future** | — | Could |
| IN-06 | Agent with tools every turn | Autonomous PF agent | **Out of scope** | ROADMAP non-goals | Won't |
| IN-07 | Local LLM extraction (vLLM) | Privacy / no cloud | **Roadmap** | ROADMAP optional | Won't (now) |
| IN-08 | Outlines for stricter JSON | Replace raw Gemini | **Roadmap** | ROADMAP optional | Won't (now) |

---

## 15. Engineering & quality (user-visible impact)

| ID | Use case | User story | Status | Phase / ref |
|----|----------|------------|--------|-------------|
| EQ-01 | Chat backend health check | App detects outage | **Implemented** | `/health`, smoke scripts |
| EQ-02 | Session survives restart | Pending not lost | **Implemented** | Phase 0, P2 sessions |
| EQ-03 | Automated regression tests | Fewer breakages | **Implemented** | 86 pytest + 67 Vitest |
| EQ-04 | Playwright E2E (English) | Critical paths guarded | **Implemented** | Phase 0, nightly CI |
| EQ-05 | Playwright E2E (Vietnamese) | Locale regressions caught | **Planned** | Phase 0.5 |
| EQ-06 | Burr FSM for complex flows | Maintainable dialogue | **Roadmap** | P3 when 7th flow |
| EQ-07 | DuckDB fast reports | Large history | **Roadmap** | P4 when slow |

---

## 16. Use case coverage matrix (by persona)

### Persona A — Vietnamese daily user (product owner)

| Must-have use case | Ready today? |
|--------------------|--------------|
| Log expense/income in Vietnamese | ❌ → Phase 0.5 |
| Confirm / discard / edit in Vietnamese | ❌ → Phase 0.5 |
| VND amounts (`triệu`, `k`, `đ`) | 🟡 → Phase 0.5 |
| Balance & spending in Vietnamese | ❌ → Phase 0.5 |
| VND + Ho Chi Minh defaults | ❌ → Phase 0.5 |
| Dashboard in Vietnamese | ❌ → Phase 0.5–1 |
| Budgets | ❌ → Phase 2 |

**Verdict:** **Not ready** for daily Vietnamese use until Phase 0.5 completes.

### Persona B — English local hobby user

| Must-have use case | Ready today? |
|--------------------|--------------|
| Full chat loop (record → confirm) | ✅ |
| Reports & dashboard | ✅ |
| CSV export | ✅ |
| Settings (currency/TZ) | ✅ |
| Budgets | ❌ Phase 2 |

**Verdict:** **Usable MVP** for personal tracking in English.

### Persona C — Hosted multi-user (future)

Requires Phase 4 (auth, Postgres, RLS, deploy) plus most of Persona A/B features.

---

## 17. Gap analysis — top 15 unmet needs (prioritized)

| Rank | Use case ID | Gap | Recommended action |
|------|-------------|-----|-------------------|
| 1 | L-01–L-09 | Vietnamese chat end-to-end | **Phase 0.5** (immediate) |
| 2 | ST-04, ST-05 | VND / locale defaults | **Phase 0.5** V-6, V-10 |
| 3 | DB-07 | UI money format ignores profile currency | Fix in Phase 0.5 or 1 |
| 4 | CM-04, CM-05 | No transaction management UI | **Phase 1** F-3, F-4 |
| 5 | DB-06 | Dashboard locked to current month | **Phase 1** F-2 |
| 6 | BG-01–BG-03 | No budgets | **Phase 2** |
| 7 | RC-01 | No recurring | **Phase 3** |
| 8 | DS-06 | No backup/restore | **Phase 1** F-6 |
| 9 | CM-07 | Cannot delete one confirmed tx | **Future** (consider Phase 1) |
| 10 | RQ-08 | No trend comparison | **Phase 1** F-1 |
| 11 | AU-01–AU-04 | No real auth / sync | **Phase 4** |
| 12 | TC-12 | No receipt OCR | **Future** (mobile) |
| 13 | MB-01–MB-02 | No mobile app | **Future** |
| 14 | IN-02 | No splits | **Future** |
| 15 | EQ-06 | Dialogue complexity cap | **Roadmap** Burr when budgets land |

---

## 18. Traceability to documents

| Document | Role |
|----------|------|
| [PRODUCT_PLAN.md](./PRODUCT_PLAN.md) | **What to build next** (Phases 0.5–5) |
| [ROADMAP.md](./ROADMAP.md) | **Engineering backlog** (Burr, DuckDB, Outlines, vLLM) |
| [ARCHITECTURE.md](./ARCHITECTURE.md) | As-built system |
| [TEST_STRATEGY.md](./TEST_STRATEGY.md) | Critical paths CP-1–CP-6 |
| [schemas/chat-payloads.json](./schemas/chat-payloads.json) | Chat response contracts |
| **This catalog** | **Complete use case inventory** |
| **Feature specs (1:1)** | [specs/README.md](./specs/README.md) — RFC per feature for PO review |

When shipping a feature, update the relevant rows in this catalog, the matching spec in `specs/`, and link the PR to the phase ID.

---

## Revision history

| Date | Change |
|------|--------|
| 2026-05-28 | Initial catalog: full use case inventory vs implemented / planned / future |
