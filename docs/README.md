# Documentation

Documentation for [Finguard](../README.md) — a local-first personal finance chat app.

## Start here

| Document | Description |
|----------|-------------|
| [PRODUCT_PLAN.md](./PRODUCT_PLAN.md) | **What to build next** — product priorities, phased roadmap, feature backlog |
| [USE_CASE_CATALOG.md](./USE_CASE_CATALOG.md) | **All user use cases** — implemented vs planned vs future |
| [ARCHITECTURE.md](./ARCHITECTURE.md) | **As-built** system design |
| [ROADMAP.md](./ROADMAP.md) | Backlog and priorities (**Burr**, **DuckDB**, semantic router, Outlines) |
| [design/chat-backend-target.md](./design/chat-backend-target.md) | **Target** chat backend (four layers) |
| [runbooks/local-development.md](./runbooks/local-development.md) | Run the app locally (`make dev`) |
| [TEST_STRATEGY.md](./TEST_STRATEGY.md) | How we test (pytest, Vitest, Playwright) |
| [TEST_COVERAGE_REPORT.md](./TEST_COVERAGE_REPORT.md) | Coverage snapshot and gaps |
| [specs/README.md](./specs/README.md) | **Feature specs** — one RFC per use case (PO build/defer/reject) |
| [decisions/](./decisions/README.md) | Architecture decision records (ADRs) |

## Reference

| Document | Description |
|----------|-------------|
| [schemas/chat-payloads.json](./schemas/chat-payloads.json) | JSON Schema for chat webhook `custom` payloads |
| [backend-query-audit.md](./backend-query-audit.md) | SQLite query scoping rules (`user_id`) |
| [runbooks/production-deploy.md](./runbooks/production-deploy.md) | Future production / hosted deploy notes |

## Repository layout

```text
docs/
├── README.md                 ← you are here
├── PRODUCT_PLAN.md           Product priorities & phased roadmap
├── USE_CASE_CATALOG.md       User use cases & implementation status
├── ARCHITECTURE.md           As-built
├── ROADMAP.md                Backlog (Burr, DuckDB, …)
├── design/                   Target design (chat backend)
├── TEST_STRATEGY.md
├── decisions/                ADRs (numbered)
├── runbooks/                 Operational how-tos
├── schemas/                  API / payload contracts
├── specs/                    Per-feature RFC specs (build_all_specs.py)
└── archive/                  Superseded plans (historical only)
```

## Archive

Do not use [archive/](./archive/README.md) for current development. It keeps earlier stack iterations (Supabase-first, Rasa CALM, prototype plans) for context only.

## Contributing

See [CONTRIBUTING.md](../CONTRIBUTING.md) at the repository root.
