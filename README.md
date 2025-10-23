# 5500 Backend

A FastAPI-based backend for QR code classroom surveys. Teachers create sessions using a global survey library, students scan QR codes to submit responses.

## Features

- **FastAPI** framework with automatic API documentation
- **Modular architecture** with separate routers for different features
- **Global Survey Library** - Shared survey templates across all teachers
- **Pydantic** models for data validation and settings management
- **Type hints** throughout the codebase with strict mypy checking
- **Development tools** including Black, Ruff, and pre-commit hooks
- **Interactive API docs** at `/docs`
- **Environment-based configuration** with Pydantic Settings

## API Endpoints

### Authentication (Teachers)
- `POST /api/auth/signup` - Teacher registration
- `POST /api/auth/login` - Teacher login

### Teacher Routes (JWT Required)
- `POST /api/courses` - Create course
- `GET /api/courses` - List teacher's courses
- `GET /api/surveys` - List available survey templates
- `POST /api/surveys` - Create new survey template
- `POST /api/sessions/{course_id}/sessions` - Create session with survey template
- `POST /api/sessions/{session_id}/close` - Close session
- `GET /api/sessions/{session_id}/submissions` - Get session submissions

### Public Routes (No Auth)
- `GET /api/public/join/{join_token}` - Get session info by token
- `POST /api/public/join/{join_token}/submit` - Submit survey response

## Global Survey Library

The system uses a **global survey library** approach where survey templates are shared across all teachers:

- **Survey Templates**: Pre-defined surveys stored in the `surveys` table
- **Session Creation**: Teachers select from available templates when creating sessions
- **Consistency**: All teachers have access to the same survey options
- **Efficiency**: No need to recreate surveys for each session

### Available Survey Templates

The system comes with two pre-seeded survey templates:

1. **Learning Style Survey A** - 8 questions about learning preferences
2. **Learning Style Survey B** - 8 questions about learning approaches

Each template includes:
- Multiple choice questions with 3 options each
- Scoring system that maps to learning categories
- Consistent structure for easy analysis

## Project Structure

```
backend/
├── app/                    # Main application package
│   ├── __init__.py
│   ├── main.py            # FastAPI application entry point
│   ├── db.py              # Database connection and session management
│   ├── core/              # Core configuration and utilities
│   │   ├── __init__.py
│   │   ├── config.py      # Application settings
│   │   └── security.py    # Password hashing and JWT utilities
│   ├── models/            # SQLAlchemy database models
│   │   ├── __init__.py
│   │   ├── teacher.py     # Teacher model
│   │   ├── course.py      # Course model
│   │   ├── class_session.py # Class session model
│   │   ├── survey_template.py # Survey template model
│   │   └── submission.py  # Submission model
│   ├── schemas/           # Pydantic schemas for API
│   │   ├── __init__.py
│   │   ├── auth.py        # Authentication schemas
│   │   ├── course.py      # Course schemas
│   │   ├── session.py     # Session schemas
│   │   ├── survey_template.py # Survey template schemas
│   │   ├── public.py      # Public API schemas
│   │   └── submission.py  # Submission schemas
│   └── api/               # API routes and dependencies
│       ├── __init__.py
│       ├── deps.py        # Dependency injection
│       └── routes/        # API route handlers
│           ├── __init__.py
│           ├── auth.py    # Authentication routes
│           ├── courses.py # Course management routes
│           ├── sessions.py # Session management routes
│           ├── surveys.py # Survey template routes
│           └── public.py  # Public API routes
├── scripts/               # Utility scripts
│   ├── init-db.sql       # Database initialization
│   └── seed.py           # Database seeding
├── tests/                 # Test files
│   └── __init__.py
├── Makefile              # Development shortcuts
├── pyproject.toml        # Project configuration and dependencies
├── uv.lock              # Dependency lock file
└── README.md            # This file
```

## Quick Start

If you already have pyenv and uv installed, you can get started quickly:

```bash
# Clone the repository (if not already done)
git clone <repository-url>
cd backend

# Set up Python environment
pyenv local 3.11.9
pyenv install 3.11.9  # if not already installed

# Install dependencies and run
make setup  # Sets up development environment
make run    # Starts the FastAPI server
```

Then visit http://localhost:8000/docs to see the interactive API documentation!

## Development Commands

The project includes a comprehensive Makefile for common development tasks:

```bash
# Setup development environment
make setup          # Install dependencies and pre-commit hooks

# Running the application
make run            # Start the FastAPI server with auto-reload
make dev            # Start complete dev environment (database + backend)

# Code quality checks
make format         # Format code with Black
make lint           # Lint code with Ruff
make typecheck      # Type checking with Mypy
make precommit      # Run pre-commit hooks on all files
make check          # Run all code quality checks

# Git workflow
make commit         # Auto-fix code and stage changes (ready for commit)
make commit-auto    # Auto-fix, stage, and commit with timestamp

# Database commands
make db-migrate     # Run database migrations
make db-seed        # Seed database with sample data
make db-reset       # Reset database (removes all data and reseeds)

# Docker commands (optional)
make docker-up      # Start PostgreSQL with Docker
make docker-pgadmin  # Start PostgreSQL + pgAdmin with Docker
make docker-full    # Start full stack (backend + database + pgAdmin)
make docker-down    # Stop Docker services
make docker-logs    # Show Docker logs
make docker-reset   # Reset database (removes all data)
make docker-rebuild # Complete rebuild: database + pgAdmin + migrate + seed
make docker-build   # Build FastAPI Docker image
make docker-run     # Run FastAPI in Docker
make db-shell       # Connect to PostgreSQL shell
make db-backup      # Create database backup

# Cleanup
make clean          # Remove temporary files and caches
```

## Prerequisites

- [pyenv](https://github.com/pyenv/pyenv) - Python version management
- [uv](https://github.com/astral-sh/uv) - Fast Python package installer and resolver
- [Docker](https://docs.docker.com/get-docker/) - For PostgreSQL database
- [Docker Compose](https://docs.docker.com/compose/install/) - For multi-container setup

## Setup Instructions

### 1. Install pyenv (if not already installed)

**macOS (using Homebrew):**
```bash
brew install pyenv
```

**Linux:**
```bash
curl https://pyenv.run | bash
```

### 2. Install uv (if not already installed)

```bash
curl -LsSf https://astral.sh/uv/install.sh | sh
```

### 3. Set up Python environment

```bash
# Install Python 3.11.9 (or latest 3.11.x)
pyenv install 3.11.9

# Set local Python version for this project
pyenv local 3.11.9

# Verify Python version
python --version
```

### 4. Set up the database

```bash
# Copy environment file
cp env.example .env

# Run database migrations
make db-migrate

# Seed the database with sample data
make db-seed
```

### 5. Install dependencies and run the application

```bash
# Install dependencies and setup development environment
make setup

# Run the FastAPI application
make run
```

Alternatively, you can run directly with uv:
```bash
# Install dependencies
uv sync

# Run the application
uv run uvicorn app.main:app --reload --port 8000
```

## Running the Application

### Option 1: Full Docker Stack (Recommended)
Run everything in Docker containers:

```bash
# Start the complete stack (backend + database + pgAdmin)
make docker-full

# Or use the development command
make dev
```

### Option 2: Local Development
Run the backend locally with Docker database:

```bash
# Start database and pgAdmin
make docker-pgadmin

# Run backend locally
make dev
```

### Access Points

Once running, you can access:

- **API Base URL**: http://localhost:8000
- **Interactive API Documentation**: http://localhost:8000/docs
- **Alternative API Documentation**: http://localhost:8000/redoc
- **PostgreSQL Database**: localhost:5432
- **pgAdmin**: http://localhost:5050 (admin@qrsurvey.com / admin_password)

## Database Management with pgAdmin

pgAdmin provides a web-based interface to manage your PostgreSQL database.

### Starting pgAdmin

```bash
# Start pgAdmin (starts both database and pgAdmin)
make docker-up

# Or start pgAdmin separately
make docker-pgadmin
```

### Accessing pgAdmin

1. **Open pgAdmin**: Go to http://localhost:5050
2. **Login**: 
   - Email: `admin@qrsurvey.com`
   - Password: `admin_password`

### Connecting to the Database

1. **Right-click "Servers"** → **"Register"** → **"Server..."**
2. **General Tab**:
   - Name: `5500 Database`
3. **Connection Tab**:
   - Host name/address: `5500_database` (or `localhost`)
   - Port: `5432`
   - Maintenance database: `qr_survey_db`
   - Username: `qr_survey_user`
   - Password: `qr_survey_password`
4. **Click "Save"**

### Useful pgAdmin Features

- **Browse Tables**: Expand your database → Schemas → public → Tables
- **Run Queries**: Use the Query Tool (SQL icon in toolbar)
- **View Data**: Right-click any table → "View/Edit Data" → "All Rows"
- **Export Data**: Right-click table → "Import/Export Data"

## Database Schema Management

### ⚠️ Important: Survey Table Naming

**Current State**: Survey data is stored in the `surveys` table (NOT `survey_templates`).

This project underwent a table rename during development:
- **OLD**: `survey_templates` table (deprecated)
- **NEW**: `surveys` table (current)

### Database Migration Guidelines

When making schema changes, follow these steps to avoid confusion:

#### 1. **Always Use Alembic Migrations**

```bash
# Create a new migration
uv run alembic revision --autogenerate -m "description of changes"

# Apply migrations
uv run alembic upgrade head

# Check migration status
uv run alembic current
```

#### 2. **Table Naming Conventions**

- **Survey Data**: Always use `surveys` table
- **Foreign Keys**: `sessions.survey_template_id` → `surveys.id`
- **Model Class**: `SurveyTemplate` (but maps to `surveys` table)

#### 3. **Before Making Changes**

```bash
# Quick database state check
uv run python scripts/check_db_state.py

# Or manual check
uv run python -c "
from app.db import get_db
from sqlalchemy import text
db = next(get_db())
result = db.execute(text('SELECT table_name FROM information_schema.tables WHERE table_schema = \\'public\\' ORDER BY table_name;'))
tables = [row[0] for row in result]
print('Current tables:', tables)
"
```

#### 4. **Common Migration Scenarios**

**Adding a Column:**
```python
# In migration file
op.add_column("surveys", sa.Column("new_field", sa.String(255), nullable=True))
```

**Renaming a Table:**
```python
# In migration file
op.rename_table("old_name", "new_name")
```

**Modifying Foreign Keys:**
```python
# Drop old constraint
op.drop_constraint("old_fk_name", "table_name", type_="foreignkey")
# Add new constraint
op.create_foreign_key("new_fk_name", "table_name", "referenced_table", ["column"], ["id"])
```

#### 5. **Verification Steps**

After any migration:

```bash
# 1. Check table exists
uv run python -c "
from app.db import get_db
from sqlalchemy import text
db = next(get_db())
result = db.execute(text('SELECT table_name FROM information_schema.tables WHERE table_schema = \\'public\\' AND table_name = \\'surveys\\';'))
exists = len(list(result)) > 0
print('surveys table exists:', exists)
"

# 2. Test API endpoints
curl -X GET http://localhost:8000/api/surveys/ -H "Authorization: Bearer $TOKEN"

# 3. Check foreign key constraints
uv run python -c "
from app.db import get_db
from sqlalchemy import text
db = next(get_db())
result = db.execute(text('''
SELECT tc.constraint_name, tc.table_name, kcu.column_name, ccu.table_name AS foreign_table_name
FROM information_schema.table_constraints AS tc 
JOIN information_schema.key_column_usage AS kcu ON tc.constraint_name = kcu.constraint_name
JOIN information_schema.constraint_column_usage AS ccu ON ccu.constraint_name = tc.constraint_name
WHERE tc.constraint_type = 'FOREIGN KEY' AND tc.table_name = 'sessions';
'''))
for row in result:
    print(f'{row[0]}: {row[1]}.{row[2]} -> {row[3]}')
"
```

#### 6. **Emergency Recovery**

If you accidentally create a `survey_templates` table:

```bash
# Check if both tables exist
uv run python -c "
from app.db import get_db
from sqlalchemy import text
db = next(get_db())
result = db.execute(text('SELECT table_name FROM information_schema.tables WHERE table_schema = \\'public\\' AND table_name IN (\\'surveys\\', \\'survey_templates\\');'))
tables = [row[0] for row in result]
print('Tables found:', tables)
"

# If both exist, migrate data and drop old table
uv run python -c "
from app.db import get_db
from sqlalchemy import text
db = next(get_db())
try:
    # Copy data from survey_templates to surveys
    db.execute(text('INSERT INTO surveys SELECT * FROM survey_templates WHERE NOT EXISTS (SELECT 1 FROM surveys WHERE surveys.id = survey_templates.id);'))
    # Drop old table
    db.execute(text('DROP TABLE survey_templates;'))
    db.commit()
    print('Migration completed successfully')
except Exception as e:
    print('Error:', e)
    db.rollback()
"
```

### Schema Reference

**Current Database Schema:**
- `teachers` - Teacher accounts
- `courses` - Teacher courses  
- `surveys` - Global survey templates (⚠️ NOT survey_templates)
- `sessions` - Class sessions (references surveys.id)
- `submissions` - Student responses with calculated scores

## Development

### Code Quality Tools

This project uses several tools to maintain code quality:

- **Black**: Code formatting with 100-character line length
- **Ruff**: Fast Python linter with auto-fixing
- **Mypy**: Static type checking with strict mode
- **Pre-commit**: Git hooks for automated quality checks

### Adding Dependencies

To add new dependencies:

```bash
# Add a new dependency
uv add package-name

# Add a development dependency
uv add --group dev package-name
```

### Configuration

The application uses Pydantic Settings for configuration management. Environment variables can be set in a `.env` file:

```bash
# .env file example
APP_NAME=5500 Backend
APP_ENV=dev
PORT=8000
```

### Running Tests

```bash
# Run tests (when you add them)
make test
# or
uv run pytest
```

## API Usage Examples

### Teacher Registration
```bash
curl -X POST "http://localhost:8000/api/auth/signup" \
     -H "Content-Type: application/json" \
     -d '{"email":"teacher@example.com","password":"Passw0rd!"}'
```

### Teacher Login
```bash
TOKEN=$(curl -s -X POST "http://localhost:8000/api/auth/login" \
     -H "Content-Type: application/json" \
     -d '{"email":"teacher1@example.com","password":"Passw0rd!"}' | jq -r .access_token)
```

### Create Course
```bash
curl -X POST "http://localhost:8000/api/courses" \
     -H "Authorization: Bearer $TOKEN" \
     -H "Content-Type: application/json" \
     -d '{"title":"CS101"}'
```

### List Available Survey Templates
```bash
curl -X GET "http://localhost:8000/api/surveys" \
     -H "Authorization: Bearer $TOKEN"
```

### Create Session with Survey Template
```bash
curl -X POST "http://localhost:8000/api/sessions/{course_id}/sessions" \
     -H "Authorization: Bearer $TOKEN" \
     -H "Content-Type: application/json" \
     -d '{"survey_template_id":"template-uuid-here"}'
```

### Public: Get Session Info
```bash
curl "http://localhost:8000/api/public/join/Ab3kZp7Q"
```

### Public: Submit Survey
```bash
curl -X POST "http://localhost:8000/api/public/join/Ab3kZp7Q/submit" \
     -H "Content-Type: application/json" \
     -d '{"student_name":"Michael","answers":{"name":"Michael","mood":"good"}}'
```

## Environment Variables

The application uses Pydantic Settings for configuration. You can set these environment variables:

- `APP_NAME`: Application name (default: "5500 Backend")
- `APP_ENV`: Environment (default: "dev")
- `PORT`: Server port (default: 8000)

Create a `.env` file in the project root to override defaults:

```bash
APP_NAME=My 5500 API
APP_ENV=production
PORT=8080
```

For production, you would typically configure:

- Database connection strings
- API keys and secrets
- Environment-specific settings
- CORS origins
- Authentication secrets

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Test your changes
5. Submit a pull request

## License

This project is part of the CS5500 final project.
