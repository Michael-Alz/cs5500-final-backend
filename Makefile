# Makefile for FastAPI backend project
# Common development shortcuts

# -------------------------------------------------
# VARIABLES
# -------------------------------------------------
PYTHON = uv run python
UV = uv run
APP = main
PORT = 8000

# -------------------------------------------------
# INSTALLATION & SETUP
# -------------------------------------------------
.PHONY: setup
setup:
	@echo "🔧 Setting up development environment..."
	uv sync
	uv run pre-commit install
	@echo "✅ Setup complete!"

# -------------------------------------------------
# RUNNING THE APP
# -------------------------------------------------
.PHONY: run
run:
	@echo "🚀 Starting FastAPI app..."
	$(UV) uvicorn $(APP):app --reload --port $(PORT)

# -------------------------------------------------
# CODE QUALITY CHECKS
# -------------------------------------------------
.PHONY: format
format:
	@echo "🎨 Running Black formatter..."
	$(UV) black .

.PHONY: lint
lint:
	@echo "🧹 Running Ruff linter..."
	$(UV) ruff check . --fix

.PHONY: typecheck
typecheck:
	@echo "🧠 Running Mypy type checks..."
	$(UV) mypy .

.PHONY: precommit
precommit:
	@echo "🔍 Running pre-commit on all files..."
	$(UV) pre-commit run --all-files

# -------------------------------------------------
# FULL CODE VALIDATION
# -------------------------------------------------
.PHONY: check
check: format lint typecheck
	@echo "✅ All code checks passed!"

# -------------------------------------------------
# CLEANUP
# -------------------------------------------------
.PHONY: clean
clean:
	@echo "🗑️ Cleaning temporary files..."
	find . -type d -name "__pycache__" -exec rm -rf {} +
	find . -type f -name "*.pyc" -delete
	find . -type f -name "*.pyo" -delete
	@echo "✨ Cleanup done."
