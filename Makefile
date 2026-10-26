# ================================================
# DoctorIn — Makefile
# ================================================
# Common development commands
# ================================================

.PHONY: help dev down build logs backend-logs frontend-logs db-shell redis-shell migrate seed test lint format clean

help: ## Show this help message
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "\033[36m%-20s\033[0m %s\n", $$1, $$2}'

# ---- Docker ----

dev: ## Start all services for local development
	docker compose up --build

down: ## Stop all services
	docker compose down

down-v: ## Stop all services and remove volumes
	docker compose down -v

build: ## Build all containers
	docker compose build

logs: ## Tail all logs
	docker compose logs -f

backend-logs: ## Tail backend logs
	docker compose logs -f backend

frontend-logs: ## Tail frontend logs
	docker compose logs -f frontend

# ---- Database ----

db-shell: ## Open PostgreSQL shell
	docker compose exec postgres psql -U doctorin -d doctorin

migrate: ## Run Alembic migrations
	docker compose exec backend alembic upgrade head

migrate-create: ## Create a new migration (usage: make migrate-create MSG="add users table")
	docker compose exec backend alembic revision --autogenerate -m "$(MSG)"

migrate-downgrade: ## Downgrade one migration
	docker compose exec backend alembic downgrade -1

seed: ## Seed database with initial data
	docker compose exec backend python -m scripts.seed

# ---- Redis ----

redis-shell: ## Open Redis CLI
	docker compose exec redis redis-cli

# ---- Testing ----

test: ## Run all backend tests
	docker compose exec backend pytest -v

test-cov: ## Run tests with coverage
	docker compose exec backend pytest --cov=app --cov-report=html -v

test-security: ## Run security tests only
	docker compose exec backend pytest tests/security/ -v

# ---- Code Quality ----

lint: ## Run linters
	docker compose exec backend ruff check app/
	cd frontend && npx next lint

format: ## Auto-format code
	docker compose exec backend ruff format app/

type-check: ## Run type checking
	cd frontend && npx tsc --noEmit

# ---- Cleanup ----

clean: ## Remove build artifacts
	find . -type d -name __pycache__ -exec rm -rf {} + 2>/dev/null || true
	find . -type d -name .pytest_cache -exec rm -rf {} + 2>/dev/null || true
	find . -type d -name .mypy_cache -exec rm -rf {} + 2>/dev/null || true
	find . -type d -name node_modules -exec rm -rf {} + 2>/dev/null || true
	find . -type d -name .next -exec rm -rf {} + 2>/dev/null || true
