# Finguard local development — lite mode (Rasa in Docker, rest on host)
# Usage: make help

SHELL := /bin/bash
ROOT := $(CURDIR)
BACKEND := $(ROOT)/backend
FRONTEND := $(ROOT)/frontend

.DEFAULT_GOAL := help

.PHONY: help install env dev down train frontend test lint health smoke migrations setup

help: ## Show targets
	@grep -E '^[a-zA-Z0-9_-]+:.*##' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*## "}; {printf "  \033[36m%-14s\033[0m %s\n", $$1, $$2}'
	@echo ""
	@echo "  Quick start: make setup && make dev"

install: ## Install pnpm + uv deps (includes LiteLLM for local dev)
	pnpm install
	cd $(BACKEND) && uv sync

env: ## Copy .env examples if missing
	@test -f $(FRONTEND)/.env.local || cp $(FRONTEND)/.env.example $(FRONTEND)/.env.local
	@test -f $(BACKEND)/.env || cp $(BACKEND)/.env.example $(BACKEND)/.env
	@echo "Edit frontend/.env.local and backend/.env, then: make dev"

dev: ## Start everything (actions + LiteLLM + Rasa + Next.js)
	@chmod +x scripts/dev-lite.sh
	@./scripts/dev-lite.sh

down: ## Stop dev-lite processes and Rasa container
	@pkill -f "uvicorn actions.server:app" 2>/dev/null || true
	@pkill -f "litellm --config" 2>/dev/null || true
	@pkill -f "mock-rasa.py" 2>/dev/null || true
	@cd $(BACKEND) && docker compose down 2>/dev/null || true
	@rm -rf .dev-lite
	@echo "Stopped."

train: ## Train Rasa (LiteLLM on host + docker compose run rasa train)
	@chmod +x scripts/train-lite.sh
	@./scripts/train-lite.sh

frontend: ## Next.js only (http://localhost:3000)
	pnpm frontend:dev

test: ## Vitest + pytest
	pnpm --dir $(FRONTEND) test
	cd $(BACKEND) && uv run pytest tests/ -q

lint: ## Biome + ruff
	pnpm --dir $(FRONTEND) exec biome check src/
	cd $(BACKEND) && uv run ruff check actions tests

health: ## Check :5055 actions, :5005 Rasa, optional :3000 Next
	@./scripts/check-health.sh

smoke: ## Unit tests + local action health (+ Docker Rasa if available)
	@./scripts/smoke-e2e.sh

migrations: ## Archived Supabase SQL apply instructions (deferred)
	@./scripts/apply-migrations.sh

setup: install env ## First-time setup
	@echo "Fill in backend/.env (GEMINI_API_KEY) and frontend/.env.local, then: make train && make dev"
