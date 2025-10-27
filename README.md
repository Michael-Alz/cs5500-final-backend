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
- `POST /api/auth/signup` - Teacher registration (email, password, full_name)
- `POST /api/auth/login` - Teacher login

### Student Authentication (NEW)
- `POST /api/students/signup` - Student registration (email, password, full_name)
- `POST /api/students/login` - Student login
- `GET /api/students/me` - Get student profile
- `GET /api/students/submissions` - Get student's submission history

### Teacher Routes (JWT Required)
- `POST /api/courses` - Create course
- `GET /api/courses` - List teacher's courses
- `POST /api/surveys` - Create new survey template
- `GET /api/surveys` - List available survey templates
- `GET /api/surveys/{survey_id}` - Get specific survey template
- `POST /api/sessions/{course_id}/sessions` - Create session with survey template
- `POST /api/sessions/{session_id}/close` - Close session
- `GET /api/sessions/{session_id}/submissions` - Get session submissions

### Public Routes (No Auth Required)
- `GET /api/public/join/{join_token}` - Get session info by token
- `POST /api/public/join/{join_token}/submit` - Submit survey response (guest or authenticated)
- `GET /api/public/join/{join_token}/submission` - Check submission status

## Global Survey Library

The system uses a **global survey library** approach where survey templates are shared across all teachers:

- **Survey Templates**: Pre-defined surveys stored in the `surveys` table
- **Session Creation**: Teachers select from available templates when creating sessions
- **Consistency**: All teachers have access to the same survey options
- **Efficiency**: No need to recreate surveys for each session

### Dynamic Scoring System

The survey system supports **dynamic categories** with flexible scoring:

- **No Hard-coded Categories**: Teachers can define any number of categories
- **Flexible Scoring**: Each option can have scores for multiple categories
- **Automatic Calculation**: The system dynamically calculates total scores per category
- **Example Categories**: `{"Active": 5, "Visual": 0, "Auditory": 0, "Passive": 0}`

#### How Dynamic Scoring Works:

1. **Survey Creation**: Teachers define categories in the `scores` field of each option
2. **Dynamic Detection**: The system automatically detects all categories from the survey template
3. **Score Calculation**: When students submit responses, scores are calculated per category
4. **Flexible Categories**: Supports any number of categories (e.g., Active, Visual, Auditory, Passive, etc.)

#### Example Survey Structure:
```json
{
  "title": "Learning Style Assessment",
  "questions": [
    {
      "id": "q1",
      "text": "I learn best when I can move around",
      "options": [
        {
          "label": "Strongly Agree",
          "scores": {"Active": 5, "Visual": 0, "Auditory": 0, "Passive": 0}
        },
        {
          "label": "Agree", 
          "scores": {"Active": 4, "Visual": 0, "Auditory": 0, "Passive": 0}
        }
      ]
    }
  ]
}
```

### Available Survey Templates

The system comes with two pre-seeded survey templates:

1. **Learning Style Survey A** - 8 questions about learning preferences
2. **Learning Style Survey B** - 8 questions about learning approaches

Each template includes:
- Multiple choice questions with 3 options each
- Scoring system that maps to learning categories
- Consistent structure for easy analysis

## Seed Data

The application comes with comprehensive seed data that demonstrates all features including the new student authentication system. Run the seed script to populate your database with test data:

```bash
# Seed the database with sample data
make db-seed

# Or run directly
uv run python scripts/seed.py
```

### Pre-seeded Test Accounts

The seed script creates the following test accounts for immediate testing:

#### **Teacher Account**
- **Email:** `teacher1@example.com`
- **Password:** `Passw0rd!`
- **Full Name:** Dr. Smith

#### **Student Accounts**
- **Student 1:** `student1@example.com` / `Passw0rd!` (Alex Johnson)
- **Student 2:** `student2@example.com` / `Passw0rd!` (Maya Chen)

### Pre-seeded Survey Templates

The seed data includes two comprehensive survey templates:

#### **1. Learning Buddy: Style Check**
- **Purpose:** Identifies learning styles and preferences
- **Questions:** 9 questions covering:
  - Physical movement preferences
  - Visual learning preferences  
  - Energy levels and emotional state
  - Learning approach preferences
- **Scoring Categories:** Active learner, Structured learner, Passive learner

#### **2. Critter Quest: Learning Adventure**
- **Purpose:** Fun, animal-themed learning style assessment
- **Questions:** 10 questions with creative animal metaphors:
  - Learning playground preferences
  - Energy levels (panda, turtle, cat, rabbit, cheetah)
  - Anxiety levels (calm ocean to storm)
  - Social learning preferences
  - Problem-solving approaches
- **Scoring Categories:** Active learner, Structured learner, Passive learner, Buddy/Social learner

### Pre-seeded Sessions

The seed data creates two active sessions with join tokens:

#### **Session 1: Learning Buddy Survey**
- **Join Token:** `LEARN123`
- **Survey:** Learning Buddy: Style Check
- **Status:** Open (active)
- **Sample Submissions:** 2 authenticated student submissions

#### **Session 2: Critter Quest Survey**
- **Join Token:** `QUEST456`
- **Survey:** Critter Quest: Learning Adventure
- **Status:** Open (active)
- **Sample Submissions:** 1 guest submission

### Sample Submissions

The seed data includes realistic sample submissions demonstrating both authentication modes:

#### **Authenticated Student Submissions**
- **Alex Johnson** (student1@example.com): Completed Learning Buddy survey
- **Maya Chen** (student2@example.com): Completed Learning Buddy survey
- Both submissions include calculated scores and are linked to student accounts

#### **Guest Submission**
- **Guest Student**: Completed Critter Quest survey
- Demonstrates guest mode functionality without authentication

### Database Schema Features Demonstrated

The seed data showcases all new features:

#### **Student Authentication System**
- Student accounts with full authentication
- JWT token-based authentication
- Student profile management
- Submission history tracking

#### **Dual Submission Modes**
- **Authenticated Mode:** Submissions linked to student accounts
- **Guest Mode:** Anonymous submissions with guest names
- Proper constraint handling (either student_id OR guest_name, not both)

#### **Survey Scoring System**
- Dynamic category detection from survey templates
- Automatic score calculation based on student responses
- Multiple learning style categories supported

#### **Session Management**
- QR code generation with join tokens
- Session status tracking (open/closed)
- Teacher course and session management

### Testing with Seed Data

You can immediately test all endpoints using the pre-seeded data:

```bash
# Test teacher authentication
curl -X POST "http://localhost:8000/api/auth/login" \
     -H "Content-Type: application/json" \
     -d '{"email":"teacher1@example.com","password":"Passw0rd!"}'

# Test student authentication  
curl -X POST "http://localhost:8000/api/students/login" \
     -H "Content-Type: application/json" \
     -d '{"email":"student1@example.com","password":"Passw0rd!"}'

# Test public session access
curl "http://localhost:8000/api/public/join/LEARN123"

# Test guest submission
curl -X POST "http://localhost:8000/api/public/join/QUEST456/submit" \
     -H "Content-Type: application/json" \
     -d '{"student_name":"Test Guest","answers":{"q1":"4 — Mostly me"},"is_guest":true}'
```

### Seed Data Reset

To reset and re-seed the database:

```bash
# Or manually clear and re-seed
uv run python scripts/seed.py
```

The seed data provides a complete demonstration environment for testing all API endpoints and features without needing to create test data manually.

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
│   │   ├── student.py     # Student model (NEW)
│   │   ├── course.py      # Course model
│   │   ├── class_session.py # Class session model
│   │   ├── survey_template.py # Survey template model
│   │   └── submission.py  # Submission model (updated for dual mode)
│   ├── schemas/           # Pydantic schemas for API
│   │   ├── __init__.py
│   │   ├── auth.py        # Teacher authentication schemas
│   │   ├── student_auth.py # Student authentication schemas (NEW)
│   │   ├── course.py      # Course schemas
│   │   ├── session.py     # Session schemas
│   │   ├── public.py      # Public API schemas (updated)
│   │   └── submission.py  # Submission schemas (updated)
│   └── api/               # API routes and dependencies
│       ├── __init__.py
│       ├── deps.py        # Dependency injection (updated with student auth)
│       └── routes/        # API route handlers
│           ├── __init__.py
│           ├── auth.py    # Teacher authentication routes
│           ├── student_auth.py # Student authentication routes (NEW)
│           ├── courses.py # Course management routes
│           ├── sessions.py # Session management routes
│           └── public.py  # Public API routes (updated for dual mode)
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

If you already have Docker installed, you can get started quickly:

```bash
# Clone the repository (if not already done)
git clone <repository-url>
cd cs5500-final-backend

# Set up Python environment
pyenv local 3.11.9
pyenv install 3.11.9  # if not already installed

# Install dependencies
make setup  # Sets up development environment

# Start the complete dev environment with Docker
make dev    # Starts backend + database + pgAdmin in Docker
```

Then visit http://localhost:8000/docs to see the interactive API documentation!

**Note**: The project now uses Docker for the entire development environment. All services (backend, database, and pgAdmin) run in Docker containers with live reload support.

## Development Commands

The project includes a comprehensive Makefile for common development tasks:

```bash
# See all available commands
make help
```

```bash
# Setup development environment
make setup          # Install dependencies and pre-commit hooks

# Running the application
make dev            # Start complete dev environment (backend + database + pgAdmin in Docker)
make docker-logs    # View logs from all services
make docker-down    # Stop all Docker services

# Code quality checks
make format         # Format code with Black
make lint           # Lint code with Ruff
make typecheck      # Type checking with Mypy
make precommit      # Run pre-commit hooks on all files
make check          # Run all code quality checks

# Git workflow
make commit         # Auto-fix code and stage changes (ready for commit)
make commit-auto    # Auto-fix, stage, and commit with timestamp

# Database commands (auto-detect Docker/local)
make db-migrate     # Run database migrations
make db-seed        # Seed database with sample data
make db-check       # Check database state
make db-status      # Show database record counts
make db-clean       # Clean all data (with confirmation)
make db-clean-force # Force clean all data (no confirmation)
make db-shell       # Connect to PostgreSQL shell
make db-backup      # Create database backup

# Docker commands (dev environment)
make docker-pgadmin  # Start PostgreSQL + pgAdmin only
make docker-full    # Start full stack (backend + database + pgAdmin)
make docker-down    # Stop Docker services
make docker-logs    # Show logs from backend and database
make docker-reset   # Reset database (removes all data)
make docker-rebuild # Complete rebuild with migrations and seeding

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
# Copy environment file for Docker development
cp .env.example.docker .env.dev.docker

# Edit .env.dev.docker file with your configuration if needed
# Default configuration uses:
# - Database: class_connect_db
# - User: class_connect_user  
# - Password: class_connect_password
# - Container name: database (internal Docker network)

# Note: Docker services use the service name 'database' instead of 'localhost'
```

### 5. Environment Configuration

The application uses environment files for configuration:

#### For Docker Development (`.env.dev.docker`):
```bash
# Application Settings
APP_NAME=5500 Backend
APP_ENV=dev
PORT=8000

# Database Configuration (use service name 'database' not 'localhost')
DATABASE_URL=postgresql+psycopg://class_connect_user:class_connect_password@database:5432/class_connect_db

# JWT Configuration
JWT_SECRET=dev_change_me
JWT_EXPIRE_HOURS=24

# CORS Settings
CORS_ORIGINS=["http://localhost:5173", "http://localhost:3000"]

# Public App URL for QR codes
PUBLIC_APP_URL=http://localhost:5173
```

**Important**: In Docker, use the service name `database` instead of `localhost` in DATABASE_URL.

### 6. Start the development environment

```bash
# Start the complete dev environment (recommended)
make dev

# This will:
# - Start backend, database, and pgAdmin in Docker
# - Run migrations and seed data
# - Show backend logs with live reload
```

## Running the Application

### Docker Development (Recommended)
Run everything in Docker containers for development:

```bash
# Start the complete dev stack (backend + database + pgAdmin)
make dev

# This starts all services with:
# - Backend with live reload (--reload flag)
# - Database with volume persistence
# - pgAdmin for database management
# - Automatic migrations and seeding
```

#### Docker Development Configuration

The Docker dev setup uses `docker-compose.dev.yml` and `.env.dev.docker`:

- **Backend Service**: Runs with live reload and volume mounts for hot reloading
- **Database Service**: PostgreSQL 15 with persistent volumes
- **Environment**: Development mode with debug logging
- **Database URL**: Uses service name `database` (not `localhost`) for internal Docker network
- **Volume Mounts**: 
  - `./app` → `/app/app` (live code reload)
  - `./alembic` → `/app/alembic` (live migration changes)

### Alternative: Local Backend with Docker Database

If you prefer to run the backend locally (outside Docker) while using Docker for the database:

```bash
# Start database and pgAdmin
make docker-pgadmin

# Set up local environment (creates .env from .env.example if needed)
# Make sure DATABASE_URL points to localhost:5432 (not 'database')
# Default connection: postgresql+psycopg://class_connect_user:class_connect_password@localhost:5432/class_connect_db

# Run backend locally with auto-reload
make run
```

**Note**: The recommended approach is to use `make dev` which runs everything in Docker with live reload support. This alternative is useful if you need to debug locally or prefer your local Python environment.

### Access Points

Once running, you can access:

- **API Base URL**: http://localhost:8000
- **Interactive API Documentation**: http://localhost:8000/docs
- **Alternative API Documentation**: http://localhost:8000/redoc
- **PostgreSQL Database**: localhost:5432 (class_connect_db)
- **pgAdmin**: http://localhost:5050 (admin@classconnect.com / admin_password)

## Database Management

### Auto-Detection of Docker vs Local Environment

The database commands automatically detect whether you're running in Docker or locally:

- **When Docker is running**: Commands run inside the Docker container (using `docker-compose exec`)
- **When Docker is not running**: Commands run locally (requires database to be exposed to host)

This means you can use the same commands regardless of your setup:

```bash
# These commands work in both Docker and local environments
make db-migrate     # Runs migrations
make db-seed        # Seeds sample data
make db-check       # Checks database state
make db-clean       # Cleans all data
```

### Docker Database Access

Since the database is not exposed to the host (for security), database scripts run inside the Docker container when available. This ensures they can connect using the internal Docker network (`database:5432`).

## Database Management with pgAdmin

pgAdmin provides a web-based interface to manage your PostgreSQL database.

### Starting pgAdmin

```bash
# Start pgAdmin (starts both database and pgAdmin)
make docker-pgadmin

# Or start full dev stack which includes pgAdmin
make dev
```

### Accessing pgAdmin

1. **Open pgAdmin**: Go to http://localhost:5050
2. **Login**: 
   - Email: `admin@classconnect.com`
   - Password: `admin_password`

### Connecting to the Database

1. **Right-click "Servers"** → **"Register"** → **"Server..."**
2. **General Tab**:
   - Name: `5500 Database`
3. **Connection Tab**:
   - Host name/address: `database` (use Docker service name, not localhost)
   - Port: `5432`
   - Maintenance database: `class_connect_db`
   - Username: `class_connect_user`
   - Password: `class_connect_password`
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
# .env.dev.docker file example (for Docker development)
APP_NAME=5500 Backend
APP_ENV=dev
PORT=8000
DATABASE_URL=postgresql+psycopg://class_connect_user:class_connect_password@database:5432/class_connect_db
```

### Running Tests

The project includes comprehensive test suites for all API endpoints:

```bash
# Run all tests
make test

# Run API endpoint tests
make test-api

# Run tests with coverage
make test-coverage

# Clean test artifacts
make test-clean
```

#### Manual Test Execution

```bash
# Run all tests
uv run pytest tests/ -v

# Run specific test file
uv run pytest tests/test_all_endpoints.py -v

# Run tests with coverage
uv run pytest tests/ --cov=app --cov-report=html

# Run individual test functions
uv run pytest tests/test_all_endpoints.py::test_all_endpoints -v
```

#### Test Files

- **`tests/test_all_endpoints.py`** - Comprehensive test suite for all API endpoints
  - Tests authentication, courses, surveys, sessions, and public endpoints
  - Includes automatic test data cleanup
  - Can be run individually or as a complete suite

#### Test Features

- **Automatic Authentication**: Tests handle JWT token management
- **Data Cleanup**: Tests automatically clean up created data
- **Comprehensive Coverage**: Tests all major API endpoints
- **Error Handling**: Tests include proper error scenarios
- **Real API Testing**: Tests against actual running API endpoints

#### Running Individual Tests

```bash
# Test all endpoints in sequence
uv run python tests/test_all_endpoints.py

# Test specific endpoint categories
uv run pytest tests/test_all_endpoints.py::test_individual_endpoints -v
```

## API Usage Examples

### Teacher Registration
```bash
curl -X POST "http://localhost:8000/api/auth/signup" \
     -H "Content-Type: application/json" \
     -d '{"email":"teacher@example.com","password":"Passw0rd!","full_name":"Dr. Smith"}'
```

### Teacher Login
```bash
TOKEN=$(curl -s -X POST "http://localhost:8000/api/auth/login" \
     -H "Content-Type: application/json" \
     -d '{"email":"teacher1@example.com","password":"Passw0rd!"}' | jq -r .access_token)
```

### Student Registration (NEW)
```bash
curl -X POST "http://localhost:8000/api/students/signup" \
     -H "Content-Type: application/json" \
     -d '{"email":"student@example.com","password":"Passw0rd!","full_name":"John Student"}'
```

### Student Login (NEW)
```bash
STUDENT_TOKEN=$(curl -s -X POST "http://localhost:8000/api/students/login" \
     -H "Content-Type: application/json" \
     -d '{"email":"student1@example.com","password":"Passw0rd!"}' | jq -r .access_token)
```

### Student Profile (NEW)
```bash
curl -X GET "http://localhost:8000/api/students/me" \
     -H "Authorization: Bearer $STUDENT_TOKEN"
```

### Student Submission History (NEW)
```bash
curl -X GET "http://localhost:8000/api/students/submissions" \
     -H "Authorization: Bearer $STUDENT_TOKEN"
```

### Create Course
```bash
curl -X POST "http://localhost:8000/api/courses" \
     -H "Authorization: Bearer $TOKEN" \
     -H "Content-Type: application/json" \
     -d '{"title":"CS101"}'
```

### Create Survey Template
```bash
curl -X POST "http://localhost:8000/api/surveys" \
     -H "Authorization: Bearer $TOKEN" \
     -H "Content-Type: application/json" \
     -d '{
       "title": "Learning Style Assessment",
       "questions": [
         {
           "id": "q1",
           "text": "I learn best when I can move around",
           "options": [
             {"label": "Strongly Agree", "scores": {"Active": 5, "Visual": 0, "Auditory": 0, "Passive": 0}},
             {"label": "Agree", "scores": {"Active": 4, "Visual": 0, "Auditory": 0, "Passive": 0}},
             {"label": "Neutral", "scores": {"Active": 3, "Visual": 0, "Auditory": 0, "Passive": 0}},
             {"label": "Disagree", "scores": {"Active": 2, "Visual": 0, "Auditory": 0, "Passive": 0}},
             {"label": "Strongly Disagree", "scores": {"Active": 1, "Visual": 0, "Auditory": 0, "Passive": 0}}
           ]
         },
         {
           "id": "q2",
           "text": "I prefer visual aids like charts and diagrams",
           "options": [
             {"label": "Strongly Agree", "scores": {"Active": 0, "Visual": 5, "Auditory": 0, "Passive": 0}},
             {"label": "Agree", "scores": {"Active": 0, "Visual": 4, "Auditory": 0, "Passive": 0}},
             {"label": "Neutral", "scores": {"Active": 0, "Visual": 3, "Auditory": 0, "Passive": 0}},
             {"label": "Disagree", "scores": {"Active": 0, "Visual": 2, "Auditory": 0, "Passive": 0}},
             {"label": "Strongly Disagree", "scores": {"Active": 0, "Visual": 1, "Auditory": 0, "Passive": 0}}
           ]
         }
       ]
     }'
```

### List Available Survey Templates
```bash
curl -X GET "http://localhost:8000/api/surveys" \
     -H "Authorization: Bearer $TOKEN"
```

### Get Specific Survey Template
```bash
curl -X GET "http://localhost:8000/api/surveys/{survey_id}" \
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

### Public: Submit Survey (Guest Mode)
```bash
curl -X POST "http://localhost:8000/api/public/join/LEARN123/submit" \
     -H "Content-Type: application/json" \
     -d '{"student_name":"Guest Student","answers":{"q1":"4 — Mostly","q2":"5 — Yes, a lot"},"is_guest":true}'
```

### Public: Submit Survey (Authenticated Student Mode)
```bash
curl -X POST "http://localhost:8000/api/public/join/LEARN123/submit" \
     -H "Authorization: Bearer $STUDENT_TOKEN" \
     -H "Content-Type: application/json" \
     -d '{"answers":{"q1":"4 — Mostly","q2":"5 — Yes, a lot"},"is_guest":false}'
```

### Public: Check Submission Status
```bash
# For guest submissions
curl "http://localhost:8000/api/public/join/LEARN123/submission?guest_name=Guest Student"

# For authenticated student submissions
curl "http://localhost:8000/api/public/join/LEARN123/submission" \
     -H "Authorization: Bearer $STUDENT_TOKEN"
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
