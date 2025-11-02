# Makefile for FastAPI backend project
# Common development shortcuts

# -------------------------------------------------
# VARIABLES
# -------------------------------------------------
PYTHON = uv run python
UV = uv run
APP = app.main
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

.PHONY: dev
dev:
	@echo "🚀 Starting development environment..."
	@echo "🐳 Starting shared services (database + pgAdmin)..."
	docker-compose -f docker-compose.dev.yml up -d database pgadmin
	@echo "⏳ Waiting for database to become healthy..."
	@until docker exec 5500_database_dev pg_isready -U class_connect_user -d class_connect_db > /dev/null 2>&1; do echo "Waiting for database..."; sleep 2; done
	@echo "🔄 Applying database migrations (head)..."
	docker-compose -f docker-compose.dev.yml run --rm backend uv run alembic upgrade head
	@echo "🌱 Seeding database with starter data..."
	docker-compose -f docker-compose.dev.yml run --rm backend uv run python scripts/seed.py
	@echo "🚀 Bringing up FastAPI backend (live reload enabled)..."
	docker-compose -f docker-compose.dev.yml up -d backend
	@echo "✅ Development environment ready!"
	@echo "📊 Database: localhost:5432"
	@echo "🌐 pgAdmin: http://localhost:5050"
	@echo "🚀 Backend: http://localhost:8000"
	@echo "📋 View logs with: make docker-logs"
	@echo "📋 Stop services with: make docker-down"
	docker-compose -f docker-compose.dev.yml logs -f backend


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
# GIT & COMMIT HELPERS
# -------------------------------------------------
.PHONY: commit
commit:
	@echo "🔧 Running pre-commit checks and auto-fixing..."
	$(UV) pre-commit run --all-files || true
	@echo "📝 Adding all changes..."
	git add .
	@echo "✅ Ready to commit! Run: git commit -m 'your message'"

.PHONY: commit-auto
commit-auto:
	@echo "🤖 Auto-committing with pre-commit fixes..."
	$(UV) pre-commit run --all-files || true
	git add .
	git commit -m "Auto-fix: $(shell date '+%Y-%m-%d %H:%M:%S')" || echo "No changes to commit"

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

# -------------------------------------------------
# DOCKER COMMANDS
# -------------------------------------------------
.PHONY: docker-up
docker-up:
	@echo "🐳 Starting 5500 database with Docker..."
	docker-compose -f docker-compose.dev.yml up -d database
	@echo "✅ 5500 database is running on localhost:5432"

.PHONY: docker-pgadmin
docker-pgadmin:
	@echo "🐳 Starting 5500 database and pgAdmin..."
	docker-compose -f docker-compose.dev.yml up -d
	@echo "✅ 5500 database is running on localhost:5432"
	@echo "✅ pgAdmin is running on localhost:5050"
	@echo "📋 Login: admin@classconnect.com / admin_password"

.PHONY: docker-full
docker-full:
	@echo "🚀 Starting full 5500 stack (backend + database + pgAdmin)..."
	docker-compose -f docker-compose.dev.yml up -d
	@echo "⏳ Waiting for services to be ready..."
	sleep 30
	@echo "🔍 Checking database connection..."
	@until docker exec 5500_database_dev pg_isready -U class_connect_user -d class_connect_db; do echo "Waiting for database..."; sleep 2; done
	@echo "🔄 Running database migrations..."
	docker-compose -f docker-compose.dev.yml exec backend uv run alembic upgrade head
	@echo "🌱 Seeding database..."
	docker-compose -f docker-compose.dev.yml exec backend uv run python scripts/seed.py
	@echo "✅ Full 5500 stack is running!"
	@echo "🚀 Backend: http://localhost:8000"
	@echo "📊 Database: localhost:5432"
	@echo "🌐 pgAdmin: http://localhost:5050"
	@echo "📋 pgAdmin Login: admin@classconnect.com / admin_password"

.PHONY: docker-down
docker-down:
	@echo "🛑 Stopping Docker services..."
	docker-compose -f docker-compose.dev.yml down
	@echo "✅ Docker services stopped"

.PHONY: docker-logs
docker-logs:
	@echo "📋 Showing Docker logs..."
	docker-compose -f docker-compose.dev.yml logs -f backend database

.PHONY: docker-reset
docker-reset:
	@echo "🔄 Resetting 5500 database..."
	docker-compose -f docker-compose.dev.yml down -v
	docker-compose -f docker-compose.dev.yml up -d database
	@echo "✅ 5500 database reset complete"

.PHONY: docker-rebuild
docker-rebuild:
	@echo "🔄 Completely rebuilding Docker environment..."
	@echo "🛑 Stopping and removing containers and volumes..."
	docker-compose -f docker-compose.dev.yml down -v
	@echo "🐳 Starting fresh development stack..."
	docker-compose -f docker-compose.dev.yml up -d
	@echo "⏳ Waiting for database to be ready..."
	sleep 20
	@echo "🔍 Checking database connection..."
	@until docker exec 5500_database_dev pg_isready -U class_connect_user -d class_connect_db; do echo "Waiting for database..."; sleep 2; done
	@echo "🔄 Running database migrations..."
	docker-compose -f docker-compose.dev.yml exec backend uv run alembic upgrade head
	@echo "🌱 Seeding database with sample data..."
	docker-compose -f docker-compose.dev.yml exec backend uv run python scripts/seed.py
	@echo "✅ Complete rebuild finished!"
	@echo "📊 Database: localhost:5432"
	@echo "🌐 pgAdmin: http://localhost:5050"
	@echo "🚀 Backend: http://localhost:8000"
	@echo "📋 Login: admin@classconnect.com / admin_password"


.PHONY: db-shell
db-shell:
	@echo "🐚 Connecting to 5500 database shell..."
	docker-compose -f docker-compose.dev.yml exec database psql -U class_connect_user -d class_connect_db

.PHONY: db-backup
db-backup:
	@echo "💾 Creating 5500 database backup..."
	docker-compose -f docker-compose.dev.yml exec database pg_dump -U class_connect_user class_connect_db > backup_$(shell date +%Y%m%d_%H%M%S).sql
	@echo "✅ Backup created"

# -------------------------------------------------
# DATABASE COMMANDS
# -------------------------------------------------
.PHONY: db-migrate
db-migrate:
	@echo "🔄 Running database migrations..."
	@if docker ps | grep -q 5500_backend_dev; then \
		echo "Running migrations in Docker container..."; \
		docker-compose -f docker-compose.dev.yml exec backend uv run alembic upgrade head; \
	elif docker ps | grep -q 5500_database_dev; then \
		echo "Running migrations via ephemeral backend container..."; \
		docker-compose -f docker-compose.dev.yml run --rm backend uv run alembic upgrade head; \
	else \
		echo "Running migrations locally..."; \
		$(UV) alembic upgrade head; \
	fi

.PHONY: db-seed
db-seed:
	@echo "🌱 Seeding database with sample data..."
	@if docker ps | grep -q 5500_backend_dev; then \
		echo "Running seed script in Docker container..."; \
		docker-compose -f docker-compose.dev.yml exec backend uv run python scripts/seed.py; \
	elif docker ps | grep -q 5500_database_dev; then \
		echo "Running seed script via ephemeral backend container..."; \
		docker-compose -f docker-compose.dev.yml run --rm backend uv run python scripts/seed.py; \
	else \
		echo "Running seed script locally..."; \
		$(UV) python scripts/seed.py; \
	fi

.PHONY: db-check
db-check:
	@echo "🔍 Checking database state..."
	@if docker ps | grep -q 5500_backend_dev; then \
		echo "Running database check in Docker container..."; \
		docker-compose -f docker-compose.dev.yml exec backend uv run python scripts/check_db_state.py; \
	elif docker ps | grep -q 5500_database_dev; then \
		echo "Running database check via ephemeral backend container..."; \
		docker-compose -f docker-compose.dev.yml run --rm backend uv run python scripts/check_db_state.py; \
	else \
		echo "Running database check locally..."; \
		$(UV) python scripts/check_db_state.py; \
	fi

.PHONY: db-clean
db-clean:
	@echo "🧹 Cleaning all data from database..."
	@if docker ps | grep -q 5500_backend_dev; then \
		echo "Running database cleanup in Docker container..."; \
		docker-compose -f docker-compose.dev.yml exec backend uv run python scripts/clean_db.py; \
	elif docker ps | grep -q 5500_database_dev; then \
		echo "Running database cleanup via ephemeral backend container..."; \
		docker-compose -f docker-compose.dev.yml run --rm backend uv run python scripts/clean_db.py; \
	else \
		echo "Running database cleanup locally..."; \
		$(UV) python scripts/clean_db.py; \
	fi

.PHONY: db-clean-force
db-clean-force:
	@echo "🧹 Force cleaning all data from database..."
	@if docker ps | grep -q 5500_backend_dev; then \
		echo "Running force database cleanup in Docker container..."; \
		docker-compose -f docker-compose.dev.yml exec backend uv run python scripts/clean_db.py --force; \
	elif docker ps | grep -q 5500_database_dev; then \
		echo "Running force database cleanup via ephemeral backend container..."; \
		docker-compose -f docker-compose.dev.yml run --rm backend uv run python scripts/clean_db.py --force; \
	else \
		echo "Running force database cleanup locally..."; \
		$(UV) python scripts/clean_db.py --force; \
	fi

.PHONY: db-status
db-status:
	@echo "📊 Checking database status..."
	@if docker ps | grep -q 5500_backend_dev; then \
		echo "Running database status check in Docker container..."; \
		docker-compose -f docker-compose.dev.yml exec backend uv run python scripts/clean_db.py --check; \
	elif docker ps | grep -q 5500_database_dev; then \
		echo "Running database status check via ephemeral backend container..."; \
		docker-compose -f docker-compose.dev.yml run --rm backend uv run python scripts/clean_db.py --check; \
	else \
		echo "Running database status check locally..."; \
		$(UV) python scripts/clean_db.py --check; \
	fi



# -------------------------------------------------
# HELP
# -------------------------------------------------
.PHONY: help
help:
	@echo "🚀 5500 Backend - Available Commands"
	@echo ""
	@echo "📦 Setup & Installation:"
	@echo "  make setup          Install dependencies and pre-commit hooks"
	@echo ""
	@echo "🏃 Running the Application:"
	@echo "  make run            Start FastAPI server with auto-reload"
	@echo "  make dev            Start complete dev environment (database + backend)"
	@echo ""
	@echo "🧪 Testing:"
	@echo "  make test            Run all tests"
	@echo "  make test-api        Run API endpoint tests"
	@echo "  make test-coverage   Run tests with coverage report"
	@echo "  make test-clean      Clean test artifacts"
	@echo ""
	@echo "🔍 Code Quality:"
	@echo "  make format          Format code with Black"
	@echo "  make lint            Lint code with Ruff"
	@echo "  make typecheck       Type checking with Mypy"
	@echo "  make check           Run all code quality checks"
	@echo ""
	@echo "🐳 Docker:"
	@echo "  make docker-up       Start database with Docker"
	@echo "  make docker-pgadmin  Start database + pgAdmin"
	@echo "  make docker-full     Start full stack (backend + database + pgAdmin)"
	@echo "  make docker-down     Stop Docker services"
	@echo "  make docker-rebuild  Complete rebuild with migrations and seeding"
	@echo ""
	@echo "🗄️ Database:"
	@echo "  make db-migrate      Run database migrations"
	@echo "  make db-seed         Seed database with sample data"
	@echo "  make db-check        Check database state"
	@echo "  make db-status       Show database record counts"
	@echo "  make db-clean        Clean all data (with confirmation)"
	@echo "  make db-clean-force  Force clean all data (no confirmation)"
	@echo "  make db-shell        Connect to database shell"
	@echo "  make db-backup       Create database backup"
	@echo ""
	@echo "🧹 Cleanup:"
	@echo "  make clean           Remove temporary files and caches"
	@echo "  make test-clean      Clean test artifacts"
	@echo ""
	@echo "📝 Git Helpers:"
	@echo "  make commit          Auto-fix code and stage changes"
	@echo "  make commit-auto     Auto-fix, stage, and commit with timestamp"

# -------------------------------------------------
# RUNNING TESTS
# -------------------------------------------------
.PHONY: test
test:
	@echo "🧪 Running all tests (inside backend container)..."
	@if ! docker compose -f docker-compose.dev.yml ps --services --filter status=running | grep -q '^backend$$'; then \
		echo "   Backend container not running – starting backend (and database)..."; \
		docker compose -f docker-compose.dev.yml up -d backend; \
		sleep 5; \
	fi
	docker compose -f docker-compose.dev.yml exec backend uv run pytest tests/ -v

.PHONY: test-api
test-api:
	@echo "🧪 Running API endpoint tests (inside backend container)..."
	@if ! docker compose -f docker-compose.dev.yml ps --services --filter status=running | grep -q '^backend$$'; then \
		echo "   Backend container not running – starting backend (and database)..."; \
		docker compose -f docker-compose.dev.yml up -d backend; \
		sleep 5; \
	fi
	docker compose -f docker-compose.dev.yml exec backend uv run pytest tests/test_api.py -v

.PHONY: test-coverage
test-coverage:
	@echo "🧪 Running tests with coverage (inside backend container)..."
	@if ! docker compose -f docker-compose.dev.yml ps --services --filter status=running | grep -q '^backend$$'; then \
		echo "   Backend container not running – starting backend (and database)..."; \
		docker compose -f docker-compose.dev.yml up -d backend; \
		sleep 5; \
	fi
	docker compose -f docker-compose.dev.yml exec backend uv run pytest tests/ --cov=app --cov-report=html --cov-report=term

.PHONY: test-watch
test-watch:
	@echo "🧪 Running tests in watch mode..."
	$(UV) pytest-watch tests/ -v

.PHONY: test-clean
test-clean:
	@echo "🧹 Cleaning test artifacts..."
	rm -rf .pytest_cache/
	rm -rf htmlcov/
	rm -rf .coverage
	@echo "✅ Test cleanup complete"
