# Finguard local development — backend on host + Next.js
# Usage: make help

SHELL := /bin/bash
ROOT := $(CURDIR)
BACKEND := $(ROOT)/backend
FRONTEND := $(ROOT)/frontend

.DEFAULT_GOAL := help

.PHONY: help install env dev down frontend test lint health smoke migrations setup

help: ## Show targets
	@grep -E '^[a-zA-Z0-9_-]+:.*##' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*## "}; {printf "  \033[36m%-14s\033[0m %s\n", $$1, $$2}'
	@echo ""
	@echo "  Quick start: make setup && make dev"

install: ## Install pnpm + uv deps
	pnpm install
	cd $(BACKEND) && uv sync

env: ## Copy .env examples if missing
	@test -f $(FRONTEND)/.env.local || cp $(FRONTEND)/.env.example $(FRONTEND)/.env.local
	@test -f $(BACKEND)/.env || cp $(BACKEND)/.env.example $(BACKEND)/.env
	@echo "Edit frontend/.env.local and backend/.env, then: make dev"

dev: ## Start backend (:5055) + Next.js
	@chmod +x scripts/dev-lite.sh
	@./scripts/dev-lite.sh

down: ## Stop dev-lite processes
	@pkill -f "uvicorn actions.server:app" 2>/dev/null || true
	@rm -rf .dev-lite
	@echo "Stopped."

frontend: ## Next.js only (http://localhost:3000)
	pnpm frontend:dev

test: ## Vitest + pytest
	pnpm --dir $(FRONTEND) test
	cd $(BACKEND) && uv run pytest tests/ -q

test-coverage: ## Unit tests with coverage reports
	pnpm --dir $(FRONTEND) test:coverage
	cd $(BACKEND) && uv run pytest tests/ -q --cov=actions --cov-report=term-missing

test-e2e: ## Playwright browser tests (starts mock stack)
	chmod +x scripts/playwright-webserver.sh
	cd $(FRONTEND) && pnpm exec playwright install chromium
	cd $(FRONTEND) && pnpm test:e2e

lint: ## Biome + ruff
	pnpm --dir $(FRONTEND) exec biome check src/
	cd $(BACKEND) && uv run ruff check actions tests

health: ## Check :5055 backend, optional :3000 Next
	@./scripts/check-health.sh

smoke: ## Unit tests + backend health
	@./scripts/smoke-e2e.sh

migrations: ## Archived Supabase SQL apply instructions (deferred)
	@./scripts/apply-migrations.sh

setup: install env ## First-time setup
	@echo "Fill in backend/.env and frontend/.env.local, then: make dev"
