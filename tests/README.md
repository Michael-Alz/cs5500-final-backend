# Test Suite

This directory contains a simplified and combined test suite for the 5500 Backend API.

## Test Structure

### `test_api.py`
A comprehensive test file that covers all API functionality:

- **Health Checks** (no database required)
- **Authentication Protection** (no database required)  
- **Input Validation** (no database required)
- **Error Handling** (no database required)
- **Teacher Authentication** (requires database)
- **Student Authentication** (requires database)
- **Course Management** (requires database)
- **Session Management** (requires database)
- **Public Endpoints** (requires database)
- **Comprehensive Flow** (requires database)

## Running Tests

### Quick Tests (No Database Required)
```bash
# Run only tests that don't require a database
uv run python -m pytest tests/test_api.py::test_health_endpoints tests/test_api.py::test_authentication_protection tests/test_api.py::test_input_validation tests/test_api.py::test_error_handling -v

# Or run all tests (will skip database-dependent tests if DB not available)
uv run python -m pytest tests/ -v
```

### Full Tests (Database Required)
```bash
# 1. Start the database
docker-compose up -d database

# 2. Run migrations
make db-migrate

# 3. Seed data
uv run python scripts/seed.py

# 4. Run all tests
uv run python -m pytest tests/ -v

# 5. Run only database tests
uv run python -m pytest tests/ -m database -v
```

### Direct Execution
```bash
# Run the test file directly
uv run python tests/test_api.py
```

## Test Categories

### Database-Independent Tests
- ✅ Health endpoint checks
- ✅ Authentication protection
- ✅ Input validation
- ✅ Error handling

### Database-Dependent Tests (marked with `@pytest.mark.database`)
- 🔄 Teacher authentication flow
- 🔄 Student authentication flow (NEW FEATURE)
- 🔄 Course management
- 🔄 Session management
- 🔄 Public survey endpoints
- 🔄 Comprehensive user flows

## Features Tested

### New Student Authentication System
- Student signup with email, password, and full name
- Student login with JWT tokens
- Student profile access
- Student submission history
- Integration with existing guest submission system

### Existing Teacher System
- Teacher authentication
- Course creation and management
- Session management
- Survey template handling

### Public API
- Guest survey submission
- Session joining via QR codes
- Survey skipping functionality
- Submission status checking

## Test Data

The tests use the following default credentials:
- **Teacher**: `teacher1@example.com` / `Passw0rd!`
- **Student**: `student1@example.com` / `Passw0rd!`

## Notes

- Tests are designed to be independent and can be run in any order
- Database-dependent tests will be skipped if the database is not available
- All tests use FastAPI's TestClient for efficient testing
- Tests include proper cleanup to avoid data pollution
