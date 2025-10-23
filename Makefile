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
	@echo "🐳 Starting database and pgAdmin..."
	docker-compose up -d
	@echo "⏳ Waiting for database to be ready..."
	sleep 10
	@echo "🔍 Checking database connection..."
	@until docker exec 5500_database pg_isready -U qr_survey_user -d qr_survey_db; do echo "Waiting for database..."; sleep 2; done
	@echo "🔄 Running migrations..."
	$(UV) alembic upgrade head
	@echo "🌱 Seeding database..."
	$(UV) python scripts/seed.py
	@echo "🚀 Starting FastAPI backend..."
	@echo "✅ Development environment ready!"
	@echo "📊 Database: localhost:5432"
	@echo "🌐 pgAdmin: http://localhost:5050"
	@echo "🚀 Backend: http://localhost:8000"
	@echo "📋 Press Ctrl+C to stop the backend"
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
	docker-compose up -d database
	@echo "✅ 5500 database is running on localhost:5432"

.PHONY: docker-pgadmin
docker-pgadmin:
	@echo "🐳 Starting 5500 database and pgAdmin..."
	docker-compose up -d
	@echo "✅ 5500 database is running on localhost:5432"
	@echo "✅ pgAdmin is running on localhost:5050"
	@echo "📋 Login: admin@qrsurvey.com / admin_password"

.PHONY: docker-full
docker-full:
	@echo "🚀 Starting full 5500 stack (backend + database + pgAdmin)..."
	docker-compose up -d
	@echo "⏳ Waiting for services to be ready..."
	sleep 30
	@echo "🔍 Checking database connection..."
	@until docker exec 5500_database pg_isready -U qr_survey_user -d qr_survey_db; do echo "Waiting for database..."; sleep 2; done
	@echo "🔄 Running database migrations..."
	docker-compose exec backend uv run alembic upgrade head
	@echo "🌱 Seeding database..."
	docker-compose exec backend uv run python scripts/seed.py
	@echo "✅ Full 5500 stack is running!"
	@echo "🚀 Backend: http://localhost:8000"
	@echo "📊 Database: localhost:5432"
	@echo "🌐 pgAdmin: http://localhost:5050"
	@echo "📋 pgAdmin Login: admin@qrsurvey.com / admin_password"

.PHONY: docker-down
docker-down:
	@echo "🛑 Stopping Docker services..."
	docker-compose down
	@echo "✅ Docker services stopped"

.PHONY: docker-logs
docker-logs:
	@echo "📋 Showing Docker logs..."
	docker-compose logs -f database

.PHONY: docker-reset
docker-reset:
	@echo "🔄 Resetting 5500 database..."
	docker-compose down -v
	docker-compose up -d database
	@echo "✅ 5500 database reset complete"

.PHONY: docker-rebuild
docker-rebuild:
	@echo "🔄 Completely rebuilding Docker environment..."
	@echo "🛑 Stopping and removing containers and volumes..."
	docker-compose down -v
	@echo "🐳 Starting fresh database and pgAdmin..."
	docker-compose up -d
	@echo "⏳ Waiting for database to be ready..."
	sleep 20
	@echo "🔍 Checking database connection..."
	@until docker exec 5500_database pg_isready -U qr_survey_user -d qr_survey_db; do echo "Waiting for database..."; sleep 2; done
	@echo "🔄 Running database migrations..."
	$(UV) alembic upgrade head
	@echo "🌱 Seeding database with sample data..."
	$(UV) python scripts/seed.py
	@echo "✅ Complete rebuild finished!"
	@echo "📊 Database: localhost:5432"
	@echo "🌐 pgAdmin: http://localhost:5050"
	@echo "📋 Login: admin@qrsurvey.com / admin_password"


.PHONY: db-shell
db-shell:
	@echo "🐚 Connecting to 5500 database shell..."
	docker-compose exec database psql -U qr_survey_user -d qr_survey_db

.PHONY: db-backup
db-backup:
	@echo "💾 Creating 5500 database backup..."
	docker-compose exec database pg_dump -U qr_survey_user qr_survey_db > backup_$(shell date +%Y%m%d_%H%M%S).sql
	@echo "✅ Backup created"

# -------------------------------------------------
# DATABASE COMMANDS
# -------------------------------------------------
.PHONY: db-migrate
db-migrate:
	@echo "🔄 Running database migrations..."
	$(UV) alembic upgrade head

.PHONY: db-check
db-check:
	@echo "🔍 Checking database state..."
	$(UV) python scripts/check_db_state.py



# -------------------------------------------------
# RUNNING TESTS
# -------------------------------------------------
test:
	@echo "🧪 Running tests..."
	uv run pytest -v