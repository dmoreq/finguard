# Finguard — Rasa CALM Backend Plan

**Date:** 2026-05-27
**Status:** Proposal
**Scope:** Python AI backend for personal financial chat using Rasa CALM + Gemini 2.0 Flash / DeepSeek V3

---

## Table of Contents

1. [Decision Summary](#1-decision-summary)
2. [Architecture Overview](#2-architecture-overview)
3. [LLM Provider Analysis](#3-llm-provider-analysis)
4. [Cost Model](#4-cost-model)
5. [Tech Stack](#5-tech-stack)
6. [Project Structure](#6-project-structure)
7. [Environment & Package Setup (uv)](#7-environment--package-setup-uv)
8. [Rasa CALM Configuration](#8-rasa-calm-configuration)
9. [Action Server — FastAPI + rasa-sdk](#9-action-server--fastapi--rasa-sdk)
10. [LiteLLM Provider Routing](#10-litellm-provider-routing)
11. [Logging — Loguru](#11-logging--loguru)
12. [DateTime Handling — Pendulum](#12-datetime-handling--pendulum)
13. [Database Layer — Supabase Python](#13-database-layer--supabase-python)
14. [Frontend ↔ Rasa Bridge](#14-frontend--rasa-bridge)
15. [Deployment Strategy](#15-deployment-strategy)
16. [Implementation Phases](#16-implementation-phases)
17. [Environment Variables Reference](#17-environment-variables-reference)

---

## 1. Decision Summary

### Why Rasa CALM

Rasa CALM (Conversational AI with Language Models, introduced in Rasa 3.7) replaces the traditional ML-trained DIET classifier with an LLM-powered command generator. The key differences from traditional Rasa:

| | Traditional Rasa | Rasa CALM |
|---|---|---|
| NLU | ML model (DIET classifier) | LLM command generation |
| Training data | 400–500 utterances required | Minimal — flow descriptions only |
| Dialog logic | Stories + Rules YAML | Flows YAML (simpler) |
| Response generation | Templates only | Optional LLM rephrasing |
| Slot filling | ML-extracted entities | LLM-extracted + guided |
| Setup effort | ~50 hours | ~15–20 hours |

### Why Gemini 2.0 Flash as Primary

- **Free tier**: 1,500 requests/day — the app uses ~40–60 requests/day (accounting for CALM's 2 internal LLM calls per message)
- **Quality**: State-of-the-art for instruction following and structured output
- **OpenAI-compatible API**: Works with Rasa CALM's LLM config with `api_base` override

### Why DeepSeek V3 as Fallback

- **Cost**: $0.07–0.27/1M input tokens (with prefix cache: near-free for repeated system prompts)
- **Quality**: Matches GPT-4o class on most benchmarks
- **OpenAI-compatible API**: Drop-in alternative, same config pattern

> **Note on naming:** The user referenced "DeepSeek V4 Flash" — as of this writing, DeepSeek's latest general model is **DeepSeek-V3**. Verify the latest available model at [platform.deepseek.com](https://platform.deepseek.com) before deployment; the config patterns below work for any version.

### Licensing Note

| Tier | CALM Features | Cost |
|---|---|---|
| **Rasa Open Source 3.x** | Full CALM flows + LLMCommandGenerator | Free |
| Rasa Developer Edition | Same + extended testing tools | Free (sign-up required) |
| Rasa Pro | Enterprise guardrails, CALM Studio, SLA | ~$1,000+/month |

For this project: **Rasa Open Source 3.9+** is sufficient and free.

---

## 2. Architecture Overview

```
┌─────────────────────────────────────────────────────────────────────┐
│  Browser                                                            │
│  ChatWorkspace  ──useChat()──▶  POST /api/chat                      │
└─────────────────────────────────────────────────────────────────────┘
                                         │
                                         │ Supabase auth check
                                         │ inject user context
                                         ▼
┌─────────────────────────────────────────────────────────────────────┐
│  Next.js Route Handler  /api/chat/route.ts                          │
│  (auth proxy — keeps Rasa URL private)                              │
└─────────────────────────────────────────────────────────────────────┘
                                         │
                                         │ POST /webhooks/rest/webhook
                                         ▼
┌─────────────────────────────────────────────────────────────────────┐
│  Rasa CALM Server  :5005                                            │
│                                                                     │
│  ① SingleStepLLMCommandGenerator                                   │
│     │  POST to LiteLLM proxy                                        │
│     ▼                                                               │
│  ┌──────────────────────────────────────────────────────────────┐  │
│  │  LiteLLM Router  :4000                                       │  │
│  │  Primary:  Gemini 2.0 Flash  (free tier)                     │  │
│  │  Fallback: DeepSeek V3       (prefix-cached, ~$0.07/1M)      │  │
│  └──────────────────────────────────────────────────────────────┘  │
│                                                                     │
│  ② FlowPolicy  — executes matched flow                             │
│                                                                     │
│  ③ Custom Action call                                               │
│     │  POST /webhook                                                │
│     ▼                                                               │
└─────────────────────────────────────────────────────────────────────┘
                                         │
                                         ▼
┌─────────────────────────────────────────────────────────────────────┐
│  Action Server (FastAPI + rasa-sdk)  :5055                          │
│                                                                     │
│  ActionRecordTransaction                                            │
│  ActionQuerySpending                                                │
│  ActionGetBalance                                                   │
│  ActionListTransactions                                             │
│  ActionDeleteTransaction                                            │
│  ActionUpdateTransaction                                            │
│                                                                     │
│  → pendulum  for date parsing / timezone handling                   │
│  → loguru    for structured logging                                 │
│  → pydantic  for slot validation                                    │
└─────────────────────────────────────────────────────────────────────┘
                                         │
                                         │ async supabase-py
                                         ▼
┌─────────────────────────────────────────────────────────────────────┐
│  Supabase Postgres                                                  │
│  transactions  │  chat_messages  │  profiles  (RLS enforced)        │
└─────────────────────────────────────────────────────────────────────┘
```

### CALM Internal Flow Per User Message

```
User: "spent $45 on groceries yesterday"
         │
         ▼  ~900 input + 150 output tokens
 ┌─────────────────────────────────────────────────────────┐
 │  LLMCommandGenerator (LLM Call 1)                       │
 │  Input:  conversation history                           │
 │          + all flow descriptions                        │
 │          + current slot state                           │
 │  Output: StartFlow(record_expense,                      │
 │           amount=45, category=groceries,                │
 │           date=yesterday)                               │
 └────────────────────┬────────────────────────────────────┘
                      │
                      ▼  custom action runs
           ActionRecordTransaction
                      │  pendulum.parse("yesterday") → 2026-05-26
                      │  supabase insert → pending_confirmation
                      ▼
           Returns: transaction_id, formatted summary
                      │
                      ▼  templated (no LLM Call 2 — cost saving)
 "Got it — $45.00 for Groceries on May 26. Confirm or edit?"
```

> **Cost optimisation**: Disable response rephrasing (LLM Call 2) and use templates for confirmations. This halves LLM usage with no quality loss for structured responses.

---

## 3. LLM Provider Analysis

### Gemini 2.0 Flash

| Property | Value |
|---|---|
| API endpoint | `https://generativelanguage.googleapis.com/v1beta/openai/` |
| OpenAI-compatible | ✅ Yes (drop-in) |
| Free tier | 1,500 req/day, 1M tokens/min |
| Paid pricing | $0.10/1M input · $0.40/1M output |
| Context window | 1M tokens |
| Strengths | Fast, instruction-following, structured output, multimodal |
| Weaknesses | Occasional refusals on financial data edge cases |
| Best for | Primary provider — free tier covers 100% of personal project usage |

### DeepSeek V3 (latest)

| Property | Value |
|---|---|
| API endpoint | `https://api.deepseek.com/v1` |
| OpenAI-compatible | ✅ Yes (drop-in) |
| Free tier | None (but very cheap) |
| Pricing (cache miss) | $0.27/1M input · $1.10/1M output |
| Pricing (cache hit) | **$0.07/1M input** · $1.10/1M output |
| Context window | 64K tokens |
| Strengths | Excellent reasoning, code, financial math; prefix caching makes repeated system prompts near-free |
| Weaknesses | Occasional latency spikes; no free tier |
| Best for | Fallback when Gemini free tier is exhausted; complex financial queries |

### Provider Routing Strategy

```
User message arrives
       │
       ▼
Is Gemini free tier available? (< 1,500 req/day)
       │
  YES ─┼──▶ Gemini 2.0 Flash  [cost: $0.00]
       │
  NO  ─┼──▶ DeepSeek V3  [cost: ~$0.07/1M input w/ cache]
       │
  ERR ─┴──▶ Retry DeepSeek → log error → return graceful fallback message
```

### Why Not Other Options

| Provider | Reason skipped |
|---|---|
| GPT-4o | 25× more expensive than Gemini for same quality |
| Claude Sonnet 3.5 | 30× more expensive; no free tier |
| GPT-4o-mini | Good but no free tier; DeepSeek V3 beats it on quality |
| Self-hosted Ollama | Good privacy story, but 7B models struggle with financial entity extraction accuracy |

---

## 4. Cost Model

**Baseline:** 20 user messages/day × 30 days = 600 messages/month
**CALM LLM calls:** 1 per message (templated responses, no rephrasing)
**Tokens per call:** ~900 input + 150 output

```
┌──────────────────────────────────────────────────────────────────────┐
│                    MONTHLY COST BREAKDOWN                            │
├──────────────────────────────────────────────────────────────────────┤
│  Rasa CALM server (Hetzner CX22, 2vCPU 4GB)   $4.50/month          │
│  Action server (same VPS, no extra cost)        $0.00/month          │
│  LiteLLM proxy (same VPS, no extra cost)        $0.00/month          │
│                                                                       │
│  Gemini 2.0 Flash (primary, free tier)          $0.00/month          │
│  DeepSeek V3 (fallback, rarely hit)            ~$0.05/month          │
│                                                                       │
│  Next.js frontend (Vercel hobby tier)           $0.00/month          │
│  Supabase (free tier, 500MB DB)                 $0.00/month          │
│                                                                       │
│  ─────────────────────────────────────────────────────────           │
│  TOTAL                                         ~$4.55/month          │
└──────────────────────────────────────────────────────────────────────┘

Scaling:
  100 messages/day  → still $4.55/month (free tier covers it)
  500 messages/day  → ~$4.55 + $1.20 DeepSeek overflow = $5.75/month
  Gemini paid threshold: >1,500 req/day (you'd need 75 messages/day × 2 calls)
```

### Prefix Caching Benefit (DeepSeek)

The system prompt (user context, financial summary, flow descriptions) is ~500 tokens and identical across calls. DeepSeek's prefix cache prices these repeated tokens at $0.07 vs $0.27/1M — an **74% reduction** on input costs when cache hits.

---

## 5. Tech Stack

### Core Services

| Component | Choice | Version | Reason |
|---|---|---|---|
| Conversation framework | Rasa CALM | 3.9+ | LLM-powered flows, less training data, open-source |
| LLM primary | Gemini 2.0 Flash | latest | Free tier (1,500 req/day), excellent quality |
| LLM fallback | DeepSeek V3 | latest | Ultra-cheap with prefix caching, OpenAI-compatible |
| LLM routing | LiteLLM | 1.55+ | Unified proxy, automatic fallback, cost tracking |
| Action server | FastAPI | 0.115+ | Async, typed, fast; wraps rasa-sdk executor |

### Python Tooling

| Tool | Choice | Version | Reason |
|---|---|---|---|
| Package manager | **uv** | 0.5+ | 10–100× faster than pip/poetry; unified lockfile; workspace support |
| Linting + formatting | **ruff** | 0.8+ | Same Astral team as uv; replaces black + flake8 + isort in one tool |
| Type checker | **pyright** | latest | Strict mode; better Pydantic v2 support than mypy |
| Logging | **loguru** | 0.7+ | Structured JSON logs, zero-config, async-safe; replaces stdlib logging |
| DateTime | **pendulum** | 3.0+ | Immutable, timezone-aware, natural language parsing ("yesterday", "last month") |
| HTTP client | **httpx** | 0.28+ | Async-native; replaces requests; used by Supabase client |
| Validation | **pydantic v2** | 2.10+ | Slot validation, response schemas; 5–50× faster than v1 |
| Testing | **pytest** + **pytest-asyncio** | 8.3+ | Async test support for action handlers |
| Environment | **python-dotenv** | 1.0+ | `.env` loading |
| Retry logic | **tenacity** | 9.0+ | Exponential backoff for LLM API calls |

### Infrastructure

| Layer | Choice | Reason |
|---|---|---|
| VPS | Hetzner CX22 (2vCPU / 4GB) | Cheapest viable host for Rasa (~€3.99/month) |
| Containerisation | Docker + Compose | Run Rasa + Action Server + LiteLLM as one stack |
| Reverse proxy | Caddy | Auto TLS, zero-config HTTPS |
| CI | GitHub Actions | Free for personal projects |

---

## 6. Project Structure

```
finguard/
├── frontend/                    # (existing Next.js app)
│
├── backend/                     # ← new Python backend
│   ├── .python-version          # 3.12
│   ├── pyproject.toml           # uv project config
│   ├── uv.lock                  # lockfile (commit this)
│   ├── .env.example
│   ├── Dockerfile
│   ├── docker-compose.yml
│   │
│   ├── rasa/                    # Rasa CALM project
│   │   ├── config.yml           # pipeline: LLMCommandGenerator + LiteLLM
│   │   ├── domain.yml           # slots, responses, session config
│   │   ├── credentials.yml      # REST channel
│   │   ├── endpoints.yml        # action server URL
│   │   ├── data/
│   │   │   └── flows/
│   │   │       ├── record_transaction.yml
│   │   │       ├── query_spending.yml
│   │   │       ├── query_balance.yml
│   │   │       └── manage_transactions.yml
│   │   └── models/              # trained models (gitignored)
│   │
│   ├── actions/                 # Action server (Python)
│   │   ├── __init__.py
│   │   ├── server.py            # FastAPI + rasa-sdk executor
│   │   ├── handlers/
│   │   │   ├── __init__.py
│   │   │   ├── record_transaction.py
│   │   │   ├── query_spending.py
│   │   │   ├── query_balance.py
│   │   │   └── manage_transactions.py
│   │   ├── db/
│   │   │   ├── __init__.py
│   │   │   ├── client.py        # Supabase async client factory
│   │   │   └── queries.py       # typed query functions
│   │   ├── models/
│   │   │   ├── __init__.py
│   │   │   ├── transaction.py   # Pydantic models
│   │   │   └── slots.py         # slot type aliases
│   │   └── utils/
│   │       ├── __init__.py
│   │       ├── dates.py         # pendulum helpers
│   │       ├── formatting.py    # currency / number formatting
│   │       └── logging.py       # loguru setup
│   │
│   ├── litellm/
│   │   └── config.yaml          # LiteLLM proxy model routing config
│   │
│   └── tests/
│       ├── __init__.py
│       ├── conftest.py
│       ├── test_handlers/
│       │   ├── test_record_transaction.py
│       │   └── test_query_spending.py
│       └── test_db/
│           └── test_queries.py
│
└── docs/
    ├── nextjs-implementation-plan.md
    ├── prototype-to-product-options.md
    └── rasa-calm-backend-plan.md    ← this file
```

---

## 7. Environment & Package Setup (uv)

### Install uv

```bash
# macOS / Linux
curl -LsSf https://astral.sh/uv/install.sh | sh

# or via pip (any Python)
pip install uv
```

### Initialize the Backend Project

```bash
cd finguard
uv init backend --python 3.12
cd backend
echo "3.12" > .python-version
```

### `pyproject.toml`

```toml
[project]
name = "finguard-backend"
version = "0.1.0"
description = "Finguard CALM action server — financial AI backend"
requires-python = ">=3.12"

dependencies = [
    # Rasa CALM
    "rasa[full]>=3.9",
    "rasa-sdk>=3.9",

    # Action server
    "fastapi>=0.115",
    "uvicorn[standard]>=0.32",

    # LLM routing
    "litellm>=1.55",

    # Database
    "supabase>=2.10",

    # Validation
    "pydantic>=2.10",
    "pydantic-settings>=2.7",

    # HTTP
    "httpx>=0.28",

    # Logging
    "loguru>=0.7",

    # DateTime
    "pendulum>=3.0",

    # Resilience
    "tenacity>=9.0",

    # Config
    "python-dotenv>=1.0",
]

[dependency-groups]
dev = [
    "pytest>=8.3",
    "pytest-asyncio>=0.24",
    "pytest-httpx>=0.35",
    "ruff>=0.8",
    "pyright>=1.1",
    "factory-boy>=3.3",          # test fixtures
]

[tool.ruff]
target-version = "py312"
line-length = 100
select = ["E", "W", "F", "I", "UP", "B", "SIM", "TCH"]

[tool.ruff.format]
quote-style = "double"

[tool.pyright]
pythonVersion = "3.12"
typeCheckingMode = "standard"

[tool.pytest.ini_options]
asyncio_mode = "auto"
testpaths = ["tests"]

[tool.uv.sources]
# Pin Rasa to a specific index if needed
```

### Common uv Commands

```bash
# Install all dependencies
uv sync

# Add a new dependency
uv add httpx

# Add a dev dependency
uv add --dev pytest-asyncio

# Run a script inside the venv
uv run python -m actions.server

# Run tests
uv run pytest

# Run Rasa commands
uv run rasa train
uv run rasa run --port 5005

# Upgrade all deps
uv lock --upgrade
```

---

## 8. Rasa CALM Configuration

### `rasa/config.yml`

```yaml
recipe: default.v1
language: en

# CALM pipeline — LLM replaces the DIET classifier
pipeline:
  - name: SingleStepLLMCommandGenerator
    llm:
      provider: openai           # litellm uses openai-compatible protocol
      model: finguard-primary    # model alias defined in litellm/config.yaml
      api_base: "http://litellm:4000"
      api_key: ${LITELLM_MASTER_KEY}
      # Tune these to control cost/quality
      temperature: 0.1           # low temperature = more deterministic slot filling
      max_tokens: 256            # commands are short; cap output tokens
    # Optional: enable multi-step for complex flows
    max_history: 10

policies:
  - name: FlowPolicy
  - name: LLMBasedRouter
    llm:
      provider: openai
      model: finguard-primary
      api_base: "http://litellm:4000"
      api_key: ${LITELLM_MASTER_KEY}
      temperature: 0.0
      max_tokens: 128
  - name: RulePolicy             # handles edge cases + fallback
```

### `rasa/domain.yml`

```yaml
version: "3.1"

session_config:
  session_expiration_time: 60    # minutes
  carry_over_slots_to_new_session: false

slots:
  # Transaction slots
  amount:
    type: float
    mappings: [{ type: from_llm }]
  category:
    type: text
    mappings: [{ type: from_llm }]
  description:
    type: text
    mappings: [{ type: from_llm }]
  transaction_date:
    type: text                   # ISO string, pendulum handles parsing
    mappings: [{ type: from_llm }]
  transaction_type:
    type: categorical
    values: ["income", "expense", "pending"]
    mappings: [{ type: from_llm }]

  # Query slots
  query_period:
    type: text                   # "this_month", "last_month", "last_7d", etc.
    mappings: [{ type: from_llm }]
  query_category:
    type: text
    mappings: [{ type: from_llm }]

  # State slots
  last_transaction_id:
    type: text
    mappings: [{ type: custom }]
  confirmation_pending:
    type: bool
    mappings: [{ type: custom }]

  # User context (injected at session start)
  user_id:
    type: text
    mappings: [{ type: custom }]
  user_currency:
    type: text
    initial_value: "USD"
    mappings: [{ type: custom }]
  user_timezone:
    type: text
    initial_value: "UTC"
    mappings: [{ type: custom }]

responses:
  utter_ask_amount:
    - text: "How much was it?"
  utter_ask_category:
    - text: "What category? (e.g. groceries, dining, transport, health)"
  utter_ask_description:
    - text: "Any note for this transaction? (or say 'skip')"
  utter_ask_transaction_date:
    - text: "When was this? (today, yesterday, or a specific date)"
  utter_clarify_failed:
    - text: "I didn't quite get that. Could you rephrase? For example: 'spent $45 on groceries' or 'how much did I spend last month?'"
  utter_default:
    - text: "I'm here to help with your finances. You can tell me about transactions or ask for spending summaries."

actions:
  - action_record_transaction
  - action_query_spending
  - action_get_balance
  - action_list_transactions
  - action_delete_transaction
  - action_update_transaction
  - action_session_start
```

### `rasa/data/flows/record_transaction.yml`

```yaml
flows:
  record_expense:
    description: >
      Record an expense (money spent). Use when user mentions paying for something,
      buying something, or spending money.
    steps:
      - collect: amount
        description: The amount spent in numbers
        rejections:
          - if: "slots.amount <= 0"
            utter: utter_ask_amount
      - collect: category
        description: >
          Spending category. Common: groceries, dining, transport, health,
          entertainment, utilities, shopping, travel, education
      - collect: description
        description: Short description of what was purchased (optional)
        ask_before_filling: false
      - collect: transaction_date
        description: >
          Date of the expense. Can be relative: "today", "yesterday",
          "last Tuesday". Defaults to today if not mentioned.
        ask_before_filling: false
      - action: action_record_transaction
        metadata:
          transaction_type: expense
      - action: utter_ask_confirmation

  record_income:
    description: >
      Record income (money received). Use when user mentions getting paid,
      receiving money, a salary, or freelance payment.
    steps:
      - collect: amount
        description: The income amount
      - collect: category
        description: Income source category (e.g. salary, freelance, investment, gift)
      - collect: description
        description: Description of the income source (optional)
        ask_before_filling: false
      - collect: transaction_date
        description: When the income was received
        ask_before_filling: false
      - action: action_record_transaction
        metadata:
          transaction_type: income
      - action: utter_ask_confirmation
```

### `rasa/data/flows/query_spending.yml`

```yaml
flows:
  query_spending_report:
    description: >
      Show spending summary, report, or breakdown. Use when user asks how much
      they spent, wants a summary, balance overview, or category breakdown.
    steps:
      - collect: query_period
        description: >
          Time period for the report. Options: this_month, last_month,
          last_7d, last_30d, ytd (year to date). Defaults to this_month.
        ask_before_filling: false
      - collect: query_category
        description: Specific category to filter by (optional, leave empty for all)
        ask_before_filling: false
      - action: action_query_spending

  get_balance:
    description: >
      Show current balance, total income vs expenses, or net worth summary.
      Use when user asks about their balance, financial status, or net total.
    steps:
      - collect: query_period
        description: Time period. Defaults to this_month.
        ask_before_filling: false
      - action: action_get_balance

  list_recent_transactions:
    description: >
      List recent transactions. Use when user wants to see their transaction
      history, recent entries, or what they recorded.
    steps:
      - collect: query_period
        description: Time period filter (optional)
        ask_before_filling: false
      - collect: query_category
        description: Category filter (optional)
        ask_before_filling: false
      - action: action_list_transactions
```

### `rasa/endpoints.yml`

```yaml
action_endpoint:
  url: "http://action-server:5055/webhook"

# Tracker store — use Redis for production, in-memory for dev
tracker_store:
  type: InMemoryTrackerStore   # switch to RedisTrackerStore for multi-instance
```

---

## 9. Action Server — FastAPI + rasa-sdk

### `actions/server.py`

```python
"""
FastAPI wrapper around rasa-sdk ActionExecutor.
Provides better observability, structured logging, and custom middleware
compared to running `rasa run actions` directly.
"""

from contextlib import asynccontextmanager

from fastapi import FastAPI, Request, Response
from fastapi.responses import JSONResponse
from loguru import logger
from rasa_sdk.executor import ActionExecutor

from actions.utils.logging import setup_logging


@asynccontextmanager
async def lifespan(app: FastAPI):
    setup_logging()
    executor = ActionExecutor()
    executor.register_package("actions.handlers")
    app.state.executor = executor
    logger.info("Action server started — registered packages: actions.handlers")
    yield
    logger.info("Action server shutting down")


app = FastAPI(title="Finguard Action Server", version="0.1.0", lifespan=lifespan)


@app.get("/health")
async def health() -> dict:
    return {"status": "ok"}


@app.post("/webhook")
async def webhook(request: Request) -> JSONResponse:
    payload = await request.json()
    action_name = payload.get("next_action", "unknown")

    logger.info("action_called", action=action_name, sender=payload.get("sender_id", ""))

    try:
        result = await app.state.executor.run(payload)
        logger.debug("action_completed", action=action_name, events=len(result.get("events", [])))
        return JSONResponse(result)
    except Exception:
        logger.exception("action_failed", action=action_name)
        return JSONResponse(
            {"error": "Action execution failed", "action": action_name},
            status_code=500,
        )
```

### `actions/handlers/record_transaction.py`

```python
"""Action: record a new transaction after CALM collects all slots."""

from typing import Any

import pendulum
from loguru import logger
from pydantic import BaseModel, field_validator
from rasa_sdk import Action, Tracker
from rasa_sdk.events import AllSlotsReset, SlotSet
from rasa_sdk.executor import CollectingDispatcher

from actions.db.client import get_supabase
from actions.db.queries import insert_transaction
from actions.models.transaction import TransactionInsert
from actions.utils.dates import parse_relative_date
from actions.utils.formatting import format_currency


class RecordTransactionSlots(BaseModel):
    """Validates slots extracted by CALM before DB write."""

    amount: float
    category: str
    description: str | None = None
    transaction_date: str | None = None
    transaction_type: str = "expense"
    user_id: str
    user_currency: str = "USD"
    user_timezone: str = "UTC"

    @field_validator("amount")
    @classmethod
    def amount_must_be_positive(cls, v: float) -> float:
        if v <= 0:
            raise ValueError("Amount must be positive")
        return round(v, 2)

    @field_validator("category")
    @classmethod
    def normalise_category(cls, v: str) -> str:
        return v.strip().lower()


class ActionRecordTransaction(Action):
    def name(self) -> str:
        return "action_record_transaction"

    async def run(
        self,
        dispatcher: CollectingDispatcher,
        tracker: Tracker,
        domain: dict[str, Any],
    ) -> list[dict]:
        transaction_type = tracker.active_flow_metadata.get("transaction_type", "expense")

        try:
            slots = RecordTransactionSlots(
                amount=tracker.get_slot("amount"),
                category=tracker.get_slot("category"),
                description=tracker.get_slot("description"),
                transaction_date=tracker.get_slot("transaction_date"),
                transaction_type=transaction_type,
                user_id=tracker.get_slot("user_id"),
                user_currency=tracker.get_slot("user_currency") or "USD",
                user_timezone=tracker.get_slot("user_timezone") or "UTC",
            )
        except ValueError as e:
            logger.warning("slot_validation_failed", error=str(e), sender=tracker.sender_id)
            dispatcher.utter_message(text=f"I couldn't process that: {e}. Could you try again?")
            return []

        # Resolve relative date using pendulum
        resolved_date = parse_relative_date(
            raw=slots.transaction_date,
            timezone=slots.user_timezone,
        )

        tx = TransactionInsert(
            user_id=slots.user_id,
            type=slots.transaction_type,
            amount=slots.amount,
            currency=slots.user_currency,
            category=slots.category,
            description=slots.description,
            transaction_date=resolved_date.to_date_string(),
            status="pending_confirmation",
            source="manual_chat",
        )

        async with get_supabase() as client:
            result = await insert_transaction(client, tx)

        logger.info(
            "transaction_created",
            tx_id=result.id,
            amount=slots.amount,
            category=slots.category,
            date=resolved_date.to_date_string(),
            sender=tracker.sender_id,
        )

        amount_fmt = format_currency(slots.amount, slots.user_currency)
        date_fmt = resolved_date.format("MMMM D")

        dispatcher.utter_message(
            json_message={
                "type": "transaction_pending",
                "transaction": {
                    "id": result.id,
                    "type": slots.transaction_type,
                    "amount": slots.amount,
                    "currency": slots.user_currency,
                    "category": slots.category,
                    "description": slots.description,
                    "date": resolved_date.to_date_string(),
                },
                "text": f"Got it — {amount_fmt} for {slots.category.title()} on {date_fmt}. Confirm or edit?",
            }
        )

        return [
            SlotSet("last_transaction_id", result.id),
            SlotSet("confirmation_pending", True),
        ]
```

---

## 10. LiteLLM Provider Routing

LiteLLM acts as a local OpenAI-compatible proxy. Rasa CALM points to it; LiteLLM routes to Gemini (primary) or DeepSeek (fallback).

### `litellm/config.yaml`

```yaml
model_list:
  # Primary: Gemini 2.0 Flash (free tier)
  - model_name: finguard-primary
    litellm_params:
      model: gemini/gemini-2.0-flash
      api_key: os.environ/GEMINI_API_KEY
      rpm: 15          # Gemini free tier: 15 RPM
      tpm: 1000000     # 1M tokens/min

  # Fallback: DeepSeek V3 (cheap with prefix caching)
  - model_name: finguard-fallback
    litellm_params:
      model: deepseek/deepseek-chat
      api_key: os.environ/DEEPSEEK_API_KEY
      # Enable prefix caching for system prompt reuse
      cache_control: true

router_settings:
  routing_strategy: "usage-based-routing-v2"
  # Auto-fallback: if Gemini rate-limited → DeepSeek
  fallbacks:
    - { finguard-primary: [finguard-fallback] }
  # Retry config
  num_retries: 2
  retry_after: 5        # seconds between retries
  # Context window fallback
  context_window_fallbacks:
    - { finguard-primary: [finguard-fallback] }

general_settings:
  master_key: os.environ/LITELLM_MASTER_KEY
  # Request logging — track cost per model
  store_model_in_db: false
  # Budget tracking (optional hard cap)
  # max_budget: 5.00     # USD/month hard stop

litellm_settings:
  # Reduce latency for short command-generation prompts
  drop_params: true      # ignore unknown params per provider
  # Log to loguru-compatible format
  json_logs: true
```

### Programmatic Fallback in Actions (when calling LLM directly)

```python
# actions/utils/llm.py
import os
from tenacity import retry, stop_after_attempt, wait_exponential
import litellm
from loguru import logger


@retry(
    stop=stop_after_attempt(3),
    wait=wait_exponential(multiplier=1, min=2, max=10),
    reraise=True,
)
async def call_llm(messages: list[dict], max_tokens: int = 256) -> str:
    """
    Direct LLM call from actions (for cases needing custom prompts,
    e.g. generating a spending insight summary).
    Routes through LiteLLM provider priority.
    """
    try:
        response = await litellm.acompletion(
            model="finguard-primary",
            api_base=os.getenv("LITELLM_API_BASE", "http://litellm:4000"),
            api_key=os.getenv("LITELLM_MASTER_KEY"),
            messages=messages,
            max_tokens=max_tokens,
            temperature=0.2,
        )
        return response.choices[0].message.content
    except litellm.RateLimitError:
        logger.warning("llm_rate_limited_switching_fallback")
        raise
    except Exception:
        logger.exception("llm_call_failed")
        raise
```

---

## 11. Logging — Loguru

### `actions/utils/logging.py`

```python
"""
Structured logging setup using loguru.
Outputs JSON in production, coloured text in development.
"""

import sys
import os
from loguru import logger


def setup_logging() -> None:
    """Configure loguru for the action server."""
    logger.remove()  # Remove default handler

    is_production = os.getenv("ENV", "development") == "production"

    if is_production:
        # JSON structured logs — parseable by Datadog, Loki, etc.
        logger.add(
            sys.stdout,
            format="{message}",
            level="INFO",
            serialize=True,        # outputs valid JSON lines
            enqueue=True,          # async-safe
        )
    else:
        # Human-readable with colour for local dev
        logger.add(
            sys.stderr,
            format="<green>{time:HH:mm:ss}</green> | <level>{level: <8}</level> | <cyan>{name}</cyan>:<cyan>{line}</cyan> — <level>{message}</level>",
            level="DEBUG",
            colorize=True,
        )

    # Also write errors to a file for post-mortem debugging
    logger.add(
        "logs/errors.log",
        level="ERROR",
        rotation="10 MB",
        retention="7 days",
        serialize=True,
    )
```

### Usage Pattern

```python
# Structured log — queryable fields, not string interpolation
logger.info("transaction_created", tx_id=tx.id, amount=tx.amount, category=tx.category)
logger.warning("slot_missing", slot="amount", sender=tracker.sender_id)
logger.exception("db_write_failed", tx_id=tx.id)  # auto-captures traceback

# Context binding — attach user context for all logs in a request
with logger.contextualize(user_id=user_id, session_id=session_id):
    logger.info("session_started")
    await some_action()
    logger.info("session_ended")
```

---

## 12. DateTime Handling — Pendulum

Pendulum replaces both `datetime` and `dateutil` with an immutable, timezone-aware, natural API.

### `actions/utils/dates.py`

```python
"""
Date parsing utilities for financial transactions.
Converts CALM slot values (relative or absolute) to resolved pendulum DateTime.
"""

from __future__ import annotations

import pendulum
from pendulum import DateTime, Duration
from loguru import logger


# Relative date aliases CALM may extract
_RELATIVE_MAP: dict[str, int] = {
    "today": 0,
    "yesterday": -1,
    "day before yesterday": -2,
}

_PERIOD_RANGES: dict[str, tuple[DateTime, DateTime]] = {}


def parse_relative_date(raw: str | None, timezone: str = "UTC") -> DateTime:
    """
    Parse a slot value that may be:
      - None / empty  → today
      - "today"       → today
      - "yesterday"   → yesterday
      - "last Tuesday"→ most recent Tuesday
      - ISO date str  → parsed as-is

    Always returns a timezone-aware DateTime in the user's timezone.
    """
    tz = pendulum.timezone(timezone)
    now = pendulum.now(tz)

    if not raw or raw.lower() in ("today", "now", ""):
        return now

    lower = raw.lower().strip()

    if lower in _RELATIVE_MAP:
        return now.add(days=_RELATIVE_MAP[lower])

    # "last <weekday>"
    if lower.startswith("last "):
        weekday_name = lower[5:].strip()
        return _last_weekday(weekday_name, now)

    # Try ISO format (CALM often resolves to ISO)
    try:
        return pendulum.parse(raw, tz=tz)
    except Exception:
        logger.warning("date_parse_fallback_to_today", raw=raw)
        return now


def _last_weekday(name: str, now: DateTime) -> DateTime:
    """Return the most recent occurrence of a named weekday."""
    weekdays = {
        "monday": 0, "tuesday": 1, "wednesday": 2,
        "thursday": 3, "friday": 4, "saturday": 5, "sunday": 6,
    }
    target = weekdays.get(name)
    if target is None:
        return now

    diff = (now.day_of_week - target) % 7 or 7
    return now.subtract(days=diff)


def period_to_date_range(period: str, timezone: str = "UTC") -> tuple[str, str]:
    """
    Convert a period alias to (start_date, end_date) ISO strings.

    Examples:
      "this_month"  → ("2026-05-01", "2026-05-27")
      "last_month"  → ("2026-04-01", "2026-04-30")
      "last_7d"     → ("2026-05-20", "2026-05-27")
      "ytd"         → ("2026-01-01", "2026-05-27")
    """
    tz = pendulum.timezone(timezone)
    now = pendulum.now(tz)

    match period:
        case "this_month":
            start = now.start_of("month")
            end = now
        case "last_month":
            start = now.subtract(months=1).start_of("month")
            end = now.subtract(months=1).end_of("month")
        case "last_7d":
            start = now.subtract(days=7)
            end = now
        case "last_30d":
            start = now.subtract(days=30)
            end = now
        case "last_3m":
            start = now.subtract(months=3)
            end = now
        case "ytd":
            start = now.start_of("year")
            end = now
        case _:
            logger.warning("unknown_period_defaulting_to_month", period=period)
            start = now.start_of("month")
            end = now

    return start.to_date_string(), end.to_date_string()
```

---

## 13. Database Layer — Supabase Python

### `actions/db/client.py`

```python
"""Async Supabase client factory with connection pooling."""

import os
from contextlib import asynccontextmanager
from typing import AsyncGenerator

from loguru import logger
from supabase import AsyncClient, acreate_client


@asynccontextmanager
async def get_supabase() -> AsyncGenerator[AsyncClient, None]:
    """
    Async context manager for Supabase client.
    Uses service role key (bypasses RLS) — safe because
    user_id is always explicitly included in queries.
    """
    client = await acreate_client(
        supabase_url=os.environ["SUPABASE_URL"],
        supabase_key=os.environ["SUPABASE_SERVICE_ROLE_KEY"],
    )
    try:
        yield client
    except Exception:
        logger.exception("supabase_client_error")
        raise
    finally:
        await client.aclose()
```

### `actions/db/queries.py`

```python
"""Typed Supabase query functions for financial data."""

from __future__ import annotations

from loguru import logger
from supabase import AsyncClient

from actions.models.transaction import TransactionInsert, TransactionRow
from actions.utils.dates import period_to_date_range


async def insert_transaction(
    client: AsyncClient,
    tx: TransactionInsert,
) -> TransactionRow:
    """Insert a pending transaction. Returns the created row."""
    response = (
        await client.table("transactions")
        .insert(tx.model_dump())
        .execute()
    )
    return TransactionRow.model_validate(response.data[0])


async def get_spending_by_category(
    client: AsyncClient,
    user_id: str,
    period: str,
    timezone: str = "UTC",
    category: str | None = None,
) -> list[dict]:
    """
    Return spending totals grouped by category for a given period.
    Runs a Postgres aggregation via RPC or direct query.
    """
    start, end = period_to_date_range(period, timezone)

    query = (
        client.table("transactions")
        .select("category, amount.sum()")
        .eq("user_id", user_id)
        .eq("type", "expense")
        .eq("status", "confirmed")
        .gte("transaction_date", start)
        .lte("transaction_date", end)
    )

    if category:
        query = query.eq("category", category)

    response = await query.execute()
    logger.debug(
        "spending_query",
        user_id=user_id,
        period=period,
        rows=len(response.data),
    )
    return response.data


async def get_balance_summary(
    client: AsyncClient,
    user_id: str,
    period: str,
    timezone: str = "UTC",
) -> dict:
    """Return total income, expenses, and net for the period."""
    start, end = period_to_date_range(period, timezone)

    response = await client.rpc(
        "get_balance_summary",
        {
            "p_user_id": user_id,
            "p_start": start,
            "p_end": end,
        },
    ).execute()

    return response.data[0] if response.data else {"income": 0, "expenses": 0, "net": 0}
```

### Supabase RPC for Balance (add to migrations)

```sql
-- supabase/migrations/20260527000001_balance_rpc.sql

create or replace function get_balance_summary(
  p_user_id uuid,
  p_start date,
  p_end date
)
returns table(income numeric, expenses numeric, net numeric)
language sql
security definer
as $$
  select
    coalesce(sum(case when type = 'income' then amount else 0 end), 0) as income,
    coalesce(sum(case when type = 'expense' then amount else 0 end), 0) as expenses,
    coalesce(sum(case when type = 'income' then amount
                      when type = 'expense' then -amount
                      else 0 end), 0) as net
  from transactions
  where user_id = p_user_id
    and status = 'confirmed'
    and transaction_date between p_start and p_end;
$$;
```

---

## 14. Frontend ↔ Rasa Bridge

The Next.js route handler acts as an authenticated proxy — it verifies the Supabase session and injects user context before forwarding to Rasa.

### `frontend/src/app/api/chat/route.ts`

```typescript
// Replace the current /api/ai/parse with a streaming Rasa bridge
import { createServerSupabaseClient } from "@/lib/supabase/server";
import { NextResponse } from "next/server";

const RASA_URL = process.env.RASA_URL ?? "http://localhost:5005";

export async function POST(request: Request) {
  const supabase = await createServerSupabaseClient();
  const { data: { user } } = await supabase.auth.getUser();

  if (!user) {
    return NextResponse.json({ error: "Unauthorized" }, { status: 401 });
  }

  const { message } = await request.json();
  if (!message?.trim()) {
    return NextResponse.json({ error: "Empty message" }, { status: 400 });
  }

  // Rasa REST channel
  const rasaResponse = await fetch(`${RASA_URL}/webhooks/rest/webhook`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({
      sender: user.id,               // Rasa uses sender_id as conversation ID
      message,
      metadata: {
        user_id: user.id,            // injected into session via action_session_start
      },
    }),
  });

  if (!rasaResponse.ok) {
    return NextResponse.json({ error: "Chat service unavailable" }, { status: 503 });
  }

  // Rasa returns an array of response objects
  const responses: Array<{ text?: string; json_message?: unknown }> = await rasaResponse.json();

  return NextResponse.json({ responses });
}
```

### Message Types the Frontend Handles

```typescript
// frontend/src/features/chat/types.ts  (extend existing)
export type RasaResponse =
  | { type: "text"; text: string }
  | {
      type: "transaction_pending";
      transaction: PendingTransaction;
      text: string;
    }
  | { type: "spending_report"; data: SpendingReport; text: string }
  | { type: "balance"; data: BalanceSummary; text: string };
```

---

## 15. Deployment Strategy

### `backend/docker-compose.yml`

```yaml
services:
  rasa:
    image: rasa/rasa:3.9-full
    volumes:
      - ./rasa:/app
      - rasa-models:/app/models
    ports:
      - "5005:5005"
    environment:
      - LITELLM_MASTER_KEY=${LITELLM_MASTER_KEY}
    command: >
      run
      --enable-api
      --cors "*"
      --port 5005
      --endpoints /app/endpoints.yml
      --credentials /app/credentials.yml
    depends_on:
      - action-server
      - litellm
    restart: unless-stopped

  action-server:
    build:
      context: .
      dockerfile: Dockerfile
    ports:
      - "5055:5055"
    environment:
      - SUPABASE_URL=${SUPABASE_URL}
      - SUPABASE_SERVICE_ROLE_KEY=${SUPABASE_SERVICE_ROLE_KEY}
      - LITELLM_API_BASE=http://litellm:4000
      - LITELLM_MASTER_KEY=${LITELLM_MASTER_KEY}
      - ENV=production
    command: uv run uvicorn actions.server:app --host 0.0.0.0 --port 5055
    restart: unless-stopped

  litellm:
    image: ghcr.io/berriai/litellm:main-stable
    volumes:
      - ./litellm/config.yaml:/app/config.yaml
    ports:
      - "4000:4000"
    environment:
      - GEMINI_API_KEY=${GEMINI_API_KEY}
      - DEEPSEEK_API_KEY=${DEEPSEEK_API_KEY}
      - LITELLM_MASTER_KEY=${LITELLM_MASTER_KEY}
    command: --config /app/config.yaml --port 4000
    restart: unless-stopped

  caddy:
    image: caddy:2-alpine
    ports:
      - "80:80"
      - "443:443"
    volumes:
      - ./Caddyfile:/etc/caddy/Caddyfile
      - caddy-data:/data
    restart: unless-stopped

volumes:
  rasa-models:
  caddy-data:
```

### `backend/Dockerfile`

```dockerfile
FROM python:3.12-slim

# Install uv
COPY --from=ghcr.io/astral-sh/uv:latest /uv /usr/local/bin/uv

WORKDIR /app

# Copy dependency files first (layer caching)
COPY pyproject.toml uv.lock ./

# Install dependencies (no dev deps in production)
RUN uv sync --frozen --no-dev

# Copy source
COPY actions/ ./actions/

EXPOSE 5055
CMD ["uv", "run", "uvicorn", "actions.server:app", "--host", "0.0.0.0", "--port", "5055"]
```

### `backend/Caddyfile`

```caddyfile
# Auto TLS + reverse proxy for Rasa REST API
rasa.yourdomain.com {
    reverse_proxy rasa:5005
    # Restrict to Next.js server only in production
    # @allowed { remote_ip YOUR_VERCEL_IP }
    # handle @allowed { reverse_proxy rasa:5005 }
}
```

### Hosting: Hetzner CX22

```bash
# One-time server setup
ssh root@YOUR_SERVER_IP

apt update && apt install -y docker.io docker-compose-v2 git
systemctl enable docker

# Clone and deploy
git clone https://github.com/you/finguard.git
cd finguard/backend

cp .env.example .env
# Edit .env with your keys

# Train Rasa model first (run locally or on server)
docker run --rm -v $(pwd)/rasa:/app rasa/rasa:3.9-full train

# Start the stack
docker compose up -d
```

---

## 16. Implementation Phases

### Phase 1 — Backend Scaffold (Week 1)
**Goal:** Running skeleton with uv, Docker, and health checks.

- [ ] `uv init backend` with `pyproject.toml`
- [ ] Docker Compose: rasa + action-server + litellm + caddy
- [ ] `actions/server.py` — FastAPI + rasa-sdk executor
- [ ] Loguru setup (`actions/utils/logging.py`)
- [ ] `/health` endpoint
- [ ] `.env.example` with all required variables
- [ ] Verify: `docker compose up` → all services healthy

### Phase 2 — LiteLLM + Gemini/DeepSeek (Week 1)
**Goal:** Rasa CALM calling Gemini 2.0 Flash via LiteLLM proxy.

- [ ] `litellm/config.yaml` — Gemini primary + DeepSeek fallback
- [ ] `rasa/config.yml` — `SingleStepLLMCommandGenerator` → LiteLLM
- [ ] Verify: send message to Rasa REST API → LLM command generated
- [ ] Log LLM provider used per request (cost tracking)
- [ ] Test fallback: disable Gemini key → confirm DeepSeek kicks in

### Phase 3 — CALM Flows (Week 2)
**Goal:** Core financial flows working end-to-end.

- [ ] `data/flows/record_transaction.yml` — expense + income
- [ ] `data/flows/query_spending.yml` — report + balance + list
- [ ] `domain.yml` — all slots and responses
- [ ] Pendulum utils: `parse_relative_date`, `period_to_date_range`
- [ ] `rasa train` → verify flows resolve correctly with test messages

### Phase 4 — Action Server + Supabase (Week 2–3)
**Goal:** Actions execute and persist data to Supabase.

- [ ] `actions/db/client.py` — async Supabase client
- [ ] `actions/db/queries.py` — insert, balance, spending queries
- [ ] Supabase migration: `get_balance_summary` RPC
- [ ] `handlers/record_transaction.py` — full slot validation + DB write
- [ ] `handlers/query_spending.py` — aggregation + formatted response
- [ ] `handlers/get_balance.py`
- [ ] `handlers/list_transactions.py`
- [ ] Unit tests for all handlers (mock Supabase client)

### Phase 5 — Frontend Integration (Week 3)
**Goal:** Next.js ChatWorkspace talks to Rasa backend.

- [ ] Replace `POST /api/ai/parse` with `POST /api/chat` (Rasa bridge)
- [ ] Update `ChatWorkspace.tsx` to handle `transaction_pending` JSON messages
- [ ] Keep existing `TransactionCard` confirm/edit/discard flow
- [ ] Verify: full chat → parse → confirm → DB → dashboard cycle

### Phase 6 — Hardening (Week 4)
**Goal:** Production-ready for private beta.

- [ ] Rate limiting on `/api/chat` (Upstash Redis or Vercel middleware)
- [ ] `action_session_start` — inject user profile (currency, timezone) into slots
- [ ] Rasa `tracker_store` → Redis (for session persistence across restarts)
- [ ] Error handling: graceful degradation when LLM down
- [ ] Playwright test: full chat-to-confirm-to-save workflow
- [ ] Monitoring: log-based cost tracking (count LLM calls per day)
- [ ] Deploy to Hetzner CX22 + Caddy TLS

---

## 17. Environment Variables Reference

### `backend/.env.example`

```bash
# ─── LLM Providers ───────────────────────────────────────────────
GEMINI_API_KEY=                    # Google AI Studio → free tier
DEEPSEEK_API_KEY=                  # platform.deepseek.com → fallback

# ─── LiteLLM ─────────────────────────────────────────────────────
LITELLM_MASTER_KEY=sk-finguard-local   # internal key for Rasa → LiteLLM auth

# ─── Supabase ────────────────────────────────────────────────────
SUPABASE_URL=https://xxxx.supabase.co
SUPABASE_SERVICE_ROLE_KEY=           # service role — never expose to frontend

# ─── Server ──────────────────────────────────────────────────────
ENV=development                    # development | production
PORT=5055

# ─── Rasa (set in endpoints.yml, here for reference) ─────────────
RASA_ACTION_SERVER_URL=http://action-server:5055/webhook
```

### `frontend/.env.local` (additions)

```bash
# Rasa backend URL — only accessible server-side in Next.js route handlers
RASA_URL=https://rasa.yourdomain.com   # production
# RASA_URL=http://localhost:5005        # local dev
```

---

## Key Decisions Log

| Decision | Choice | Rationale |
|---|---|---|
| Rasa CALM vs traditional Rasa | CALM | No training data; LLM handles NLU |
| Primary LLM | Gemini 2.0 Flash | Free tier covers 100% of personal-project usage |
| Fallback LLM | DeepSeek V3 | Cheapest capable model; prefix caching for system prompts |
| LLM routing | LiteLLM proxy | Automatic fallback, cost tracking, provider-agnostic |
| Action server | FastAPI + rasa-sdk | Loguru integration, custom middleware, typed |
| Package manager | uv | 10–100× faster than pip; workspace + lockfile |
| Linter/formatter | ruff | Replaces black + flake8 + isort; same Astral ecosystem as uv |
| Logging | loguru | Zero-config structured JSON; replaces stdlib logging |
| DateTime | pendulum | Relative date parsing ("yesterday", "last month"); immutable |
| Response rephrasing | **Disabled** | Saves 1 LLM call per message (50% cost reduction); templates are sufficient for confirmations |
| Hosting | Hetzner CX22 | Cheapest VPS with enough RAM for Rasa (4GB) |
| Total monthly cost | ~$4.55 | $4.50 VPS + ~$0.05 DeepSeek fallback; Gemini free tier handles primary load |
