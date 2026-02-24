UV := uv
PACKAGE := pydantypes
SRC := src/$(PACKAGE)

.DEFAULT_GOAL := help

.PHONY: help env install init sync format format-check lint lint-fix typecheck test test-cov check docs-serve docs-build docs-deploy build clean pre-commit

##@ Setup
help: ## Show this help
	@awk 'BEGIN {FS = ":.*##"; printf "\nUsage:\n  make \033[36m<target>\033[0m\n"} /^[a-zA-Z_-]+:.*?##/ { printf "  \033[36m%-20s\033[0m %s\n", $$1, $$2 } /^##@/ { printf "\n\033[1m%s\033[0m\n", substr($$0, 5) }' $(MAKEFILE_LIST)

env: ## Create virtual environment
	$(UV) venv

install: ## Install package with all dependency groups
	$(UV) sync --all-groups

init: env install pre-commit ## Full setup: env + install + pre-commit

sync: ## Sync all dependencies from lockfile
	$(UV) sync --all-groups

##@ Quality
format: ## Format code with ruff
	$(UV) run ruff format $(SRC) tests
	$(UV) run ruff check --fix --fix-only $(SRC) tests

format-check: ## Check formatting (CI mode)
	$(UV) run ruff format --check $(SRC) tests

lint: ## Lint code with ruff
	$(UV) run ruff check $(SRC) tests

lint-fix: ## Lint and auto-fix
	$(UV) run ruff check --fix $(SRC) tests

typecheck: ## Type check with mypy
	$(UV) run mypy $(SRC)

##@ Testing
test: ## Run tests
	$(UV) run pytest tests -v

test-cov: ## Run tests with coverage
	$(UV) run pytest tests -v --cov=$(PACKAGE) --cov-report=term-missing --cov-report=html

##@ Combined
check: format-check lint typecheck test ## Run all checks: format + lint + typecheck + test

##@ Docs
docs-serve: ## Serve docs locally
	$(UV) run mkdocs serve

docs-build: ## Build docs
	$(UV) run mkdocs build --strict

docs-deploy: ## Deploy docs to GitHub Pages
	$(UV) run mkdocs gh-deploy --force

##@ Build
build: clean ## Build package
	$(UV) build

clean: ## Remove build artifacts and caches
	rm -rf build/ dist/ *.egg-info src/*.egg-info
	rm -rf .pytest_cache .mypy_cache htmlcov .coverage .coverage.*
	find . -type d -name __pycache__ -exec rm -rf {} + 2>/dev/null || true

##@ Hooks
pre-commit: ## Install pre-commit hooks
	$(UV) run pre-commit install
