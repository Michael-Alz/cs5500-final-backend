# CS5500 Final Project Backend

A FastAPI-based RESTful API backend for the CS5500 final project - a classroom engagement system with personalized activities.

## Features

- **FastAPI** framework with automatic API documentation
- **Modular architecture** with separate routers for different features
- **Pydantic** models for data validation and settings management
- **Type hints** throughout the codebase with strict mypy checking
- **Development tools** including Black, Ruff, and pre-commit hooks
- **Interactive API docs** at `/docs`
- **Environment-based configuration** with Pydantic Settings

## API Endpoints

### Core Endpoints
- `GET /` - Root endpoint with welcome message
- `GET /health` - Health check endpoint with environment info

### Authentication
- `POST /auth/signup` - User registration (demo)

### Students
- `GET /students/` - List all students (demo)

## Project Structure

```
backend/
├── app/                    # Main application package
│   ├── __init__.py
│   ├── main.py            # FastAPI application entry point
│   ├── core/              # Core configuration and utilities
│   │   ├── __init__.py
│   │   └── config.py      # Application settings
│   ├── models/            # Database models (future)
│   │   └── __init__.py
│   ├── routers/           # API route handlers
│   │   ├── __init__.py
│   │   ├── auth.py        # Authentication routes
│   │   └── students.py    # Student management routes
│   └── schemas/           # Pydantic schemas (future)
│       └── __init__.py
├── tests/                  # Test files
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

# Code quality checks
make format         # Format code with Black
make lint           # Lint code with Ruff
make typecheck      # Type checking with Mypy
make precommit      # Run pre-commit hooks on all files
make check          # Run all code quality checks

# Git workflow
make commit         # Auto-fix code and stage changes (ready for commit)
make commit-auto    # Auto-fix, stage, and commit with timestamp

# Cleanup
make clean          # Remove temporary files and caches
```

## Prerequisites

- [pyenv](https://github.com/pyenv/pyenv) - Python version management
- [uv](https://github.com/astral-sh/uv) - Fast Python package installer and resolver

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

### 4. Install dependencies and run the application

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

Once the application is running, you can access:

- **API Base URL**: http://localhost:8000
- **Interactive API Documentation**: http://localhost:8000/docs
- **Alternative API Documentation**: http://localhost:8000/redoc

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
APP_NAME=Classroom Backend
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

### Health Check
```bash
curl -X GET "http://localhost:8000/health"
```

### User Registration (Demo)
```bash
curl -X POST "http://localhost:8000/auth/signup" \
     -H "Content-Type: application/json"
```

### List Students (Demo)
```bash
curl -X GET "http://localhost:8000/students/"
```

### Root Endpoint
```bash
curl -X GET "http://localhost:8000/"
```

## Environment Variables

The application uses Pydantic Settings for configuration. You can set these environment variables:

- `APP_NAME`: Application name (default: "Classroom Backend")
- `APP_ENV`: Environment (default: "dev")
- `PORT`: Server port (default: 8000)

Create a `.env` file in the project root to override defaults:

```bash
APP_NAME=My Classroom API
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
