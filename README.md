# CS5500 Final Project Backend

A FastAPI-based RESTful API backend for the CS5500 final project.

## Features

- **FastAPI** framework with automatic API documentation
- **RESTful API** endpoints for CRUD operations
- **Pydantic** models for data validation
- **Type hints** throughout the codebase
- **Interactive API docs** at `/docs`

## API Endpoints

- `GET /` - Root endpoint with welcome message
- `GET /health` - Health check endpoint
- `GET /items` - Get all items
- `GET /items/{item_id}` - Get specific item by ID
- `POST /items` - Create new item
- `PUT /items/{item_id}` - Update existing item
- `DELETE /items/{item_id}` - Delete item
- `GET /items/search/{name}` - Search items by name

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
uv sync
uv run python main.py
```

Then visit http://localhost:8000/docs to see the interactive API documentation!

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
# Install dependencies using uv
uv sync

# Activate the virtual environment
source .venv/bin/activate

# Run the FastAPI application
uv run python main.py
```

Alternatively, you can run directly with uv:
```bash
uv run python main.py
```

## Running the Application

Once the application is running, you can access:

- **API Base URL**: http://localhost:8000
- **Interactive API Documentation**: http://localhost:8000/docs
- **Alternative API Documentation**: http://localhost:8000/redoc

## Development

### Project Structure

```
backend/
├── main.py              # FastAPI application
├── pyproject.toml       # Project configuration and dependencies
├── README.md           # This file
└── .python-version     # Python version specification
```

### Adding Dependencies

To add new dependencies:

```bash
# Add a new dependency
uv add package-name

# Add a development dependency
uv add --dev package-name
```

### Running Tests

```bash
# Run tests (when you add them)
uv run pytest
```

## API Usage Examples

### Create an item
```bash
curl -X POST "http://localhost:8000/items" \
     -H "Content-Type: application/json" \
     -d '{
       "name": "Sample Item",
       "description": "A sample item for testing",
       "price": 29.99,
       "is_available": true
     }'
```

### Get all items
```bash
curl -X GET "http://localhost:8000/items"
```

### Get a specific item
```bash
curl -X GET "http://localhost:8000/items/1"
```

### Update an item
```bash
curl -X PUT "http://localhost:8000/items/1" \
     -H "Content-Type: application/json" \
     -d '{
       "name": "Updated Item Name",
       "price": 39.99
     }'
```

### Delete an item
```bash
curl -X DELETE "http://localhost:8000/items/1"
```

## Environment Variables

Currently, the application uses in-memory storage for demo purposes. For production, you would typically configure:

- Database connection strings
- API keys
- Environment-specific settings

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Test your changes
5. Submit a pull request

## License

This project is part of the CS5500 final project.
