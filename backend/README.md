# Finguard Backend — Rasa CALM Action Server

Python backend for Finguard's personal financial chat using **Rasa CALM 3.9+** with **Gemini 2.0 Flash** / **DeepSeek V3** LLM routing.

## Quick Start

### Prerequisites

- Python 3.12+
- Docker & Docker Compose
- API keys:
  - Gemini: [Google AI Studio](https://aistudio.google.com) (free)
  - DeepSeek: [platform.deepseek.com](https://platform.deepseek.com) (optional, ~$0.05/month)
  - Supabase: Project from frontend setup

### Setup

1. **Install uv** (if not already installed)
   ```bash
   curl -LsSf https://astral.sh/uv/install.sh | sh
   ```

2. **Install dependencies**
   ```bash
   cd backend
   uv sync
   ```
   Generates `uv.lock`. The action server uses **rasa-sdk** only (full Rasa runs in Docker).
   `websockets>=13` is overridden so **supabase-py** works alongside rasa-sdk.

3. **Set up environment**
   ```bash
   cp .env.example .env
   # Edit .env with your API keys and Supabase URL
   ```

4. **Start all services**
   ```bash
   docker compose up
   ```

   Services will be available at:
   - **Rasa**: http://localhost:5005
   - **Action Server**: http://localhost:5055
   - **LiteLLM**: http://localhost:4000
   - **Caddy**: http://localhost:80

### Verify stack (no API keys required for unit tests)

```bash
./scripts/verify-stack.sh
uv run pytest tests/
```

### Testing with Rasa (requires Docker + `.env` API keys)

```bash
# Test Rasa REST API
curl -X POST http://localhost:5005/webhooks/rest/webhook \
  -H "Content-Type: application/json" \
  -d '{
    "sender": "test-user",
    "message": "spent $45 on groceries"
  }'

# Check action server health
curl http://localhost:5055/health
```

## Project Structure

```
backend/
├── pyproject.toml              # uv project config
├── actions/
│   ├── server.py              # FastAPI + rasa-sdk entry point
│   ├── handlers/              # 6 custom action classes
│   ├── db/                    # Supabase client & queries
│   ├── models/                # Pydantic schemas
│   └── utils/                 # Logging, dates, formatting
├── rasa/
│   ├── config.yml             # CALM pipeline + policies
│   ├── domain.yml             # Slots, responses, actions
│   ├── credentials.yml        # REST channel
│   ├── endpoints.yml          # Action server URL
│   ├── data/
│   │   ├── flows/             # record + query skills
│   │   └── manage_transactions/  # confirm / discard / edit skill
│   └── tests/                 # CALM e2e test cases (rasa test e2e)
├── litellm/
│   └── config.yaml            # Gemini/DeepSeek routing
├── Dockerfile                 # Docker image for action server
├── docker-compose.yml         # Full stack (Rasa + actions + LiteLLM + Caddy)
└── Caddyfile                  # Reverse proxy config
```

## Development

### Add a dependency
```bash
uv add package-name
```

### Run linting
```bash
uv run ruff check actions/ tests/
uv run ruff format actions/ tests/
```

### Run type checking
```bash
uv run pyright actions/
```

### Run tests
```bash
uv run pytest tests/
```

### Train Rasa model (if needed)
```bash
docker run --rm -v $(pwd)/rasa:/app rasa/rasa:3.9-full train
```

## Architecture

See `../docs/rasa-calm-backend-plan.md` for full design documentation.

### Key Components

1. **Rasa CALM Server** — LLM-powered conversational AI
   - `SingleStepLLMCommandGenerator` converts user messages → structured commands
   - `FlowPolicy` executes CALM flows (record expense, query spending, etc.)
   - `LLMBasedRouter` determines which flow to activate

2. **Action Server** — Custom business logic
   - FastAPI + rasa-sdk
   - 6 action handlers: record, query, balance, list, delete, session_start
   - Loguru for structured logging

3. **LiteLLM Proxy** — Unified LLM routing
   - Primary: Gemini 2.0 Flash (free tier)
   - Fallback: DeepSeek V3 (cheap with caching)
   - Auto-fallback on rate limits

4. **Supabase** — Persistent data layer
   - Transactions table with RLS
   - User profiles (currency, timezone)
   - Custom `get_balance_summary()` RPC

## Cost Model

| Component | Cost |
|---|---|
| Hetzner CX22 VPS | $4.50/month |
| Gemini 2.0 Flash | $0.00 (free tier: 1,500 req/day) |
| DeepSeek V3 fallback | ~$0.05/month (rarely hit) |
| **Total** | **~$4.55/month** |

## Deployment

### Local Docker Compose
```bash
docker compose up
```

### Production (Hetzner)
```bash
ssh root@YOUR_SERVER_IP
git clone https://github.com/you/finguard.git
cd finguard/backend
cp .env.example .env
# Edit .env with production credentials
docker compose up -d
```

## Documentation

- **`../docs/rasa-calm-backend-plan.md`** — Full architecture, config, implementation phases
- **`../docs/IMPLEMENTATION_TRACKER.md`** — Progress tracker, session notes
- **`pyproject.toml`** — Dependencies and tool configuration

## Support

See `../docs/IMPLEMENTATION_TRACKER.md` for how to ask for help and resume work.
