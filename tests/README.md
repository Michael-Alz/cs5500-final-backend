# Test Suite Overview

This directory hosts both integration tests (`test_api.py`) and focused unit tests for
service helpers (`test_services.py`). Together they exercise the entire backend stack:

- Authentication for teachers & students (signup, login, profiles, auth guards).
- Course lifecycle (creation, baseline swaps, recommendations, dashboards).
- Activity library & activity-type registry (admin-only creation, CRUD, validation).
- Session/public flows (QR join, guest + student submissions, baseline enforcement,
  recommendation feedback, dashboards, closing sessions).
- Service helpers for survey scoring, recommendation fallback logic, and submission/profile
  management.

## Test Modules

### `test_api.py`

End-to-end tests using FastAPI's `TestClient` to hit real endpoints.

- **Smoke tests**: health endpoints, missing-auth guards, validation errors.
- **Auth flows**: teacher & student signup/login, protected resource access, bad credentials.
- **Course lifecycle**: baseline survey creation, course creation & patching, activity type +
  activity CRUD (with permission checks), recommendation updates & validation.
- **Session/public flow**: forced rebaseline, public join responses, error handling for missing
  payload data, guest + authenticated submissions, recommendation payload verification,
  submission upsert behaviour, dashboard aggregation, session closure handling.

All DB-dependent tests are marked with `@pytest.mark.database`.

### `test_services.py`

Unit tests for pure service helpers using an in-memory SQLite database:

- Survey utilities (`compute_total_scores`, `determine_learning_style`, etc.).
- Recommendation fallback precedence (`style+mood`, style-default, mood-default, random, none).
- Recommendation response payload formatting.
- Submission upsert behaviour, profile toggling, and helper lookups.

## Running the Tests

### Without Database

Only the smoke tests run without a database:

```bash
uv run pytest tests/test_api.py::test_health_and_auth_guards -v
```

### With Database (recommended)

1. Start Postgres (and optionally the backend stack):

   ```bash
   make dev  # or docker compose -f docker-compose.dev.yml up -d database
   ```

2. Apply migrations & seed data (if needed):

   ```bash
   make db-migrate
   make db-seed
   ```

3. Run the full suite:

   ```bash
   make test           # runs every test
   make test-api       # integration tests only
   make test-coverage  # coverage report
   ```

Database-dependent tests are automatically skipped if they cannot connect to the DB; otherwise
they expect a clean schema.

### Targeted Runs

Run just the service/unit tests:

```bash
uv run pytest tests/test_services.py -v
```

Or filter by marker:

```bash
uv run pytest tests/ -m "database" -v
```

## Test Data Assumptions

- Tests create their own teachers/students using unique email addresses.
- Admin-restricted endpoints rely on `settings.admin_emails`; the tests patch this via
  `monkeypatch` so they do not leak state between runs.
- No test relies on pre-seeded data, but the seed script inserts helpful defaults for
  manual verification (`make db-seed`).

## Maintenance Tips

- Add new endpoints to the integration suite to ensure regression coverage.
- Keep the in-memory SQLite fixture aligned with SQLAlchemy models when new tables are added.
- Any new service helper should have a corresponding unit test.
