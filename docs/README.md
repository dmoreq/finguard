# Documentation

Documentation for [Finguard](../README.md) — a local-first personal finance chat app.

## Start here

| Document | Description |
|----------|-------------|
| [ARCHITECTURE.md](./ARCHITECTURE.md) | System design and component responsibilities |
| [runbooks/local-development.md](./runbooks/local-development.md) | Run the app locally (`make dev`) |
| [TEST_STRATEGY.md](./TEST_STRATEGY.md) | How we test (pytest, Vitest, Playwright) |
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
├── ARCHITECTURE.md
├── TEST_STRATEGY.md
├── decisions/                ADRs (numbered)
├── runbooks/                 Operational how-tos
├── schemas/                  API / payload contracts
└── archive/                  Superseded plans (historical only)
```

## Archive

Do not use [archive/](./archive/README.md) for current development. It keeps earlier stack iterations (Supabase-first, Rasa CALM, prototype plans) for context only.

## Contributing

See [CONTRIBUTING.md](../CONTRIBUTING.md) at the repository root.
