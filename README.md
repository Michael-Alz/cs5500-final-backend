# 5500 Classroom Engagement Backend

FastAPI backend that powers a classroom engagement platform. Teachers spin up class sessions,
students join via QR codes or links, and the system tracks mood, survey responses, and recommended
follow-up activities based on learning styles.

## Architecture at a Glance

- **FastAPI** app with modular routers (`auth`, `courses`, `sessions`, `public`, `activities`, etc.).
- **SQLAlchemy + Alembic** for models & migrations.
- **Pydantic** schemas for validation & configuration (see `app/schemas/` and `app/core/config.py`).
- **PostgreSQL** as the primary database (JSON columns are used extensively).
- **Unit and integration tests** under `tests/` (FastAPI `TestClient` + sqlite in-memory for services).

### Core Actors

| Actor   | Auth? | Description |
|---------|-------|-------------|
| Teacher | JWT   | Owns courses, creates sessions, configures recommendations. |
| Student | JWT   | Authenticates separately from teachers, can join sessions without guest mode. |
| Guest   | None  | Anonymous submissions via join link/QR code (name captured for display only). |

### Key Domain Objects

- **Course**: Owned by a teacher. Stores baseline survey template, mood labels, learning-style
  categories, and a `requires_rebaseline` flag that forces the next session to include a survey.
- **ClassSession**: Single meeting for a course. Holds join token, mood schema, whether the survey is
  required, and a snapshot of the baseline survey used that day.
- **Submission**: Stores mood, survey answers, computed total scores, and whether the submission
  updated the participant's baseline profile.
- **CourseStudentProfile**: Historical record per (course, student/guest) of the most recent learning
  style, scores, and submission that produced it. Only one profile per participant is marked as
  `is_current=True`.
- **ActivityType**: Registry of allowed activity templates (required/optional fields, sample payload).
- **Activity**: Reusable activity content authored by teachers (references an `ActivityType`).
- **CourseRecommendation**: Mapping of `(learning_style, mood)` to an `Activity` with fallback
  support (style default, mood default, random course activity).

## API Surface

### Teacher Authentication
| Method | Endpoint               | Description |
|--------|------------------------|-------------|
| POST   | `/api/auth/signup`     | Register a teacher. |
| POST   | `/api/auth/login`      | Obtain a JWT. |

### Student Authentication
| Method | Endpoint                     | Description |
|--------|------------------------------|-------------|
| POST   | `/api/students/signup`       | Register a student. |
| POST   | `/api/students/login`        | Obtain a student JWT. |
| GET    | `/api/students/me`           | Profile of the authenticated student. |
| GET    | `/api/students/submissions`  | Student submission history (sorted newest first). |

### Courses & Recommendations (Teacher JWT required)
| Method | Endpoint                                      | Description |
|--------|-----------------------------------------------|-------------|
| POST   | `/api/courses`                                | Create a course with baseline survey + mood labels. |
| GET    | `/api/courses`                                | List teacher's courses. |
| PATCH  | `/api/courses/{course_id}`                    | Update title / swap baseline survey (auto-flags rebaseline). |
| GET    | `/api/courses/{course_id}/recommendations`    | Fetch mood/style mappings + course metadata. |
| PATCH  | `/api/courses/{course_id}/recommendations`    | Upsert recommendation mappings (validates moods & styles). |

### Sessions (Teacher JWT required)
| Method | Endpoint                                      | Description |
|--------|-----------------------------------------------|-------------|
| POST   | `/api/sessions/{course_id}/sessions`          | Create a new class session. Enforces rebaseline when required. |
| POST   | `/api/sessions/{session_id}/close`            | Soft-close a session (blocks new submissions). |
| GET    | `/api/sessions/{session_id}/submissions`      | List submissions for a session. |
| GET    | `/api/sessions/{session_id}/dashboard`        | Aggregated mood + participant recommendations for teachers. |

### Activity Library
| Method | Endpoint                 | Description |
|--------|--------------------------|-------------|
| GET    | `/api/activity-types`    | Public list of available activity types. |
| POST   | `/api/activity-types`    | Admin-only creation of a new activity type (based on `settings.admin_emails`). |
| GET    | `/api/activities`        | List activities (filterable via `?type=`). |
| POST   | `/api/activities`        | Create activity (teacher JWT required). Validates required fields from the type. |
| GET    | `/api/activities/{id}`   | Fetch details for a single activity. |
| PATCH  | `/api/activities/{id}`   | Update activity (creator-only). |

### Public Join & Submission Flow
| Method | Endpoint                                      | Description |
|--------|-----------------------------------------------|-------------|
| GET    | `/api/public/join/{join_token}`               | Retrieve session info (mood schema + survey snapshot when required). |
| POST   | `/api/public/join/{join_token}/submit`        | Submit mood (and answers when required). Supports guests and authenticated students. |
| GET    | `/api/public/join/{join_token}/submission`    | Check if a participant submitted already (guest ID or student token). |

### Surveys
| Method | Endpoint                 | Description |
|--------|--------------------------|-------------|
| POST   | `/api/surveys`           | Create a survey template. |
| GET    | `/api/surveys`           | List survey templates (newest first). |
| GET    | `/api/surveys/{survey}`  | Fetch a single survey template. |

## Database Entities (Summary)

- `teachers`, `students`
- `courses` (baseline survey, learning-style categories, mood labels, rebaseline flag)
- `surveys` (question schema persisted as JSON)
- `sessions` (survey snapshot, mood schema, join token)
- `submissions` (answers JSON, total scores JSON, mood, baseline update flag)
- `course_student_profiles` (historical and current learning-style profiles)
- `activity_types`, `activities`
- `course_recommendations`

Refer to `alembic/versions/0f5cd2e44944_expand_learning_profiles_and_activities.py` for full
schema changes.

## Seeding & Data Utilities

Scripts live in `scripts/` and are documented in `scripts/README.md`.

Quick summary:

| Command            | Description |
|--------------------|-------------|
| `make db-migrate`  | Run Alembic migrations (executes inside container when available). |
| `make db-seed`     | Seed the DB with teacher & student accounts, surveys, sessions, submissions, **and** default activity types plus sample activities. |
| `make db-clean`    | Truncate every application table (metadata-driven, preserves schema). |
| `make db-status`   | Display record counts across all application tables. |

The seed script (`scripts/seed.py`) is idempotent: rerunning it skips existing activity types,
activities, and recommendations, updating only what is missing.

## Development Workflow

1. **Spin up services & migrate**

   ```bash
   make dev              # starts postgres, applies migrations, seeds, runs backend
   # or run manually:
   docker compose -f docker-compose.dev.yml up -d database
   make db-migrate
   make db-seed
   ```

2. **Iterate on code**: FastAPI reload is enabled in the dev container.

3. **Testing**

   ```bash
   make test           # entire suite
   make test-api       # integration tests only
   make test-coverage  # coverage report
   ```

   See `tests/README.md` for detailed guidance and test breakdown.

4. **Cleanup** (optional)

   ```bash
   make db-clean       # wipe data, keep schema (prompts)
   make db-clean-force # same but without prompt
   ```

## Notable Service Helpers

- `app/services/surveys.py` – derive learning-style categories, compute total scores, reshape survey
  snapshots for the public API.
- `app/services/recommendations.py` – implements the fallback chain for matching activities and
  builds response payloads.
- `app/services/submissions.py` – single upsert path for submissions, plus management of
  `course_student_profiles` when a baseline is updated.

Unit tests for these helpers live in `tests/test_services.py` and run entirely against an
in-memory SQLite database (no external dependencies).

## Testing Quickstart

1. Ensure services are up: `make dev`.
2. Run `make test` (or `uv run pytest tests/ -v`).
3. For ad-hoc smoke checks without a DB: `uv run pytest tests/test_api.py::test_health_and_auth_guards`.

The integration tests will automatically skip database-marked tests if the connection fails.

## Admin Notes

Activity-type creation is restricted to admin teachers. Configure admins by setting
`ADMIN_EMAILS` (ENV var) or editing `.env.dev.docker`. Tests use `monkeypatch` to temporarily
set `settings.admin_emails`.

## Contributing Tips

- When adding new endpoints, include schemas in `app/schemas/` and add matching tests.
- All changes that touch the database must include an Alembic migration.
- Keep seed data idempotent; tests rely on being able to reseed without duplicates.
- Prefer service helpers in `app/services/` for complex logic; unit test them in isolation.

Enjoy building productive classrooms! 🎓
