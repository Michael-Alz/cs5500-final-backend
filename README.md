# 5500 ClassConnect Backend

FastAPI backend that powers a classroom engagement platform. Teachers spin up class sessions,
students join via QR codes or links, and the system tracks mood, survey responses, and recommended
follow-up activities based on learning styles.

## Architecture at a Glance

-   **FastAPI** app with modular routers (`auth`, `courses`, `sessions`, `public`, `activities`, etc.).
-   **SQLAlchemy + Alembic** for models & migrations.
-   **Pydantic** schemas for validation & configuration (see `app/schemas/` and `app/core/config.py`).
-   **PostgreSQL** as the primary database (JSON columns are used extensively).
-   **Unit and integration tests** under `tests/` (FastAPI `TestClient` + sqlite in-memory for services).

## Quick Start

If you already have Docker installed, you can get started quickly:

```bash
# Clone the repository (if not already done)
git clone https://github.com/Michael-Alz/cs5500-final-backend.git
cd cs5500-final-backend

# Set the local Python version (installs 3.11.9 if missing)
pyenv install 3.11.9
pyenv local 3.11.9

# Install dependencies and development tooling
make setup

# Copy environment configuration required by Docker Compose
cp .env.example.docker .env.dev.docker

# Start the complete dev environment (backend + database + pgAdmin)
make dev
```

Then visit `http://localhost:8000/docs` for interactive API documentation.

> Note: The entire development environment runs inside Docker with live reload. Copying `.env.example.docker` to `.env.dev.docker` before running `make dev` is required because the compose file consumes that env file.

## Database Management with pgAdmin

pgAdmin provides a web-based interface to manage the PostgreSQL database used by the app.

### Starting pgAdmin

```bash
# Start pgAdmin (starts both database and pgAdmin)
make docker-pgadmin

# Or start the full dev stack which includes pgAdmin
make dev
```

### Accessing pgAdmin

-   Open http://localhost:5050 in your browser.
-   Log in with `admin@classconnect.com` / `admin_password` (configured in `docker-compose.dev.yml`).

### Connecting to the Database

1. Right-click **Servers** → **Register** → **Server...**.
2. General tab:
    - **Name:** `5500 Database`
3. Connection tab:
    - **Host name/address:** `database` (Docker service name)
    - **Port:** `5432`
    - **Maintenance database:** `class_connect_db`
    - **Username:** `class_connect_user`
    - **Password:** `class_connect_password`
4. Click **Save** to store the connection.

### Useful pgAdmin Features

-   Browse tables via **Servers → 5500 Database → Databases → class_connect_db → Schemas → public → Tables**.
-   Run SQL with the Query Tool (toolbar SQL icon).
-   View data by right-clicking a table → **View/Edit Data → All Rows**.
-   Export or import data by right-clicking a table → **Import/Export Data**.

### Core Actors

| Actor   | Auth? | Description                                                                   |
| ------- | ----- | ----------------------------------------------------------------------------- |
| Teacher | JWT   | Owns courses, creates sessions, configures recommendations.                   |
| Student | JWT   | Authenticates separately from teachers, can join sessions without guest mode. |
| Guest   | None  | Anonymous submissions via join link/QR code (name captured for display only). |

### Key Domain Objects

-   **Course**: Owned by a teacher. Stores baseline survey template, mood labels, learning-style
    categories, and a `requires_rebaseline` flag that forces the next session to include a survey.
-   **ClassSession**: Single meeting for a course. Holds join token, mood schema, whether the survey is
    required, and a snapshot of the baseline survey used that day.
-   **Submission**: Stores mood, survey answers, computed total scores, and whether the submission
    updated the participant's baseline profile.
-   **CourseStudentProfile**: Historical record per (course, student/guest) of the most recent learning
    style, scores, and submission that produced it. Only one profile per participant is marked as
    `is_current=True`.
-   **ActivityType**: Registry of allowed activity templates (required/optional fields, sample payload).
-   **Activity**: Reusable activity content authored by teachers (references an `ActivityType`).
-   **CourseRecommendation**: Mapping of `(learning_style, mood)` to an `Activity` with fallback
    support (style default, mood default, random course activity).

## API Reference

**Base URL:** `http://localhost:8000`

-   All responses are JSON encoded UTF-8.
-   Send `Content-Type: application/json` on requests with bodies.
-   Teacher routes require `Authorization: Bearer <JWT from /api/teachers/login>`.
-   Student routes require `Authorization: Bearer <JWT from /api/students/login>`.
-   IDs are UUID strings serialized as plain text; treat them as opaque identifiers.
-   Maintenance routes under `/api/admin` are only enabled when `APP_ENV` is `dev` or `test` and check `MAINTENANCE_ADMIN_PASSWORD`.

### Error Details

FastAPI validation failures follow Pydantic's error format. Domain guards raise `HTTPException` with a `detail` string (or structured object) that the frontend can interpret:

-   `AUTH_EMAIL_EXISTS`, `AUTH_INVALID_CREDENTIALS`
-   `ADMIN_DISABLED`, `ADMIN_PASSWORD_NOT_CONFIGURED`, `INVALID_PASSWORD`
-   `ADMIN_ONLY`, `ACTIVITY_TYPE_EXISTS`
-   `ACTIVITY_NOT_FOUND`, `ACTIVITY_TYPE_NOT_FOUND`, `ACTIVITY_TYPE_MISSING`, `NOT_ACTIVITY_CREATOR`
-   `MISSING_REQUIRED_FIELDS`, `CONTENT_JSON_MUST_BE_OBJECT`
-   `COURSE_NOT_FOUND`, `COURSE_ACCESS_DENIED`, `COURSE_TITLE_EXISTS`, `COURSE_MOOD_LABELS_NOT_CONFIGURED`, `COURSE_BASELINE_NOT_SET`
-   `SURVEY_TEMPLATE_NOT_FOUND`, `Survey template not found`
-   `MOOD_LABELS_REQUIRED`, `UNKNOWN_LEARNING_STYLE:<value>`, `UNKNOWN_MOOD:<value>`
-   `SESSION_NOT_FOUND`, `SESSION_ALREADY_CLOSED`, `SESSION_CLOSED`
-   `INVALID_MOOD_LABEL`, `ANSWERS_REQUIRED`, `GUEST_NAME_REQUIRED`

Unless noted, success responses use `200 OK`.

### Health & Metadata

#### GET /

-   Auth: none
-   Returns:
    ```json
    { "message": "5500 Backend is running!" }
    ```

#### GET /health

-   Auth: none
-   Returns:
    ```json
    { "status": "ok", "env": "dev" }
    ```

#### GET /favicon.ico

-   Auth: none
-   Returns an empty string to keep browsers from logging 404s.

### Teacher Authentication

#### POST /api/teachers/signup

-   Auth: none
-   Request body:
    ```json
    {
    	"email": "prof@example.edu",
    	"password": "Supersafe123",
    	"full_name": "Prof. Ada Lovelace"
    }
    ```
-   Response 200:
    ```json
    {
    	"id": "8f1b96f2-8df4-4bb3-bfda-bc3f9c9f4c27",
    	"email": "prof@example.edu",
    	"full_name": "Prof. Ada Lovelace"
    }
    ```
-   Failure codes: `400 AUTH_EMAIL_EXISTS`.

#### POST /api/teachers/login

-   Auth: none
-   Request body:
    ```json
    {
    	"email": "prof@example.edu",
    	"password": "Supersafe123"
    }
    ```
-   Response 200:
    ```json
    {
    	"access_token": "<jwt>",
    	"token_type": "bearer"
    }
    ```
-   Failure codes: `401 AUTH_INVALID_CREDENTIALS`.

### Student Authentication

#### POST /api/students/signup

-   Auth: none
-   Request body:
    ```json
    {
    	"email": "student@example.edu",
    	"password": "MySecret123",
    	"full_name": "Jordan Student"
    }
    ```
-   Response 200 mirrors teacher signup.
-   Failure codes: `400 AUTH_EMAIL_EXISTS`.

#### POST /api/students/login

-   Auth: none
-   Request body mirrors teacher login.
-   Response 200 matches the teacher login token shape.
-   Failure codes: `401 AUTH_INVALID_CREDENTIALS`.

#### GET /api/students/me

-   Auth: student bearer token.
-   Response 200:
    ```json
    {
    	"id": "e54e9f57-4df1-4468-9f7f-0b6a3cb3fc7e",
    	"email": "student@example.edu",
    	"full_name": "Jordan Student",
    	"created_at": "2024-02-14T18:22:49.123456+00:00"
    }
    ```

#### GET /api/students/submissions

-   Auth: student bearer token.
-   Returns most recent submissions in reverse chronological order.
-   Response 200:
    ```json
    {
    	"submissions": [
    		{
    			"id": "59d8b6bb-4e3b-4f28-a854-91771b65d2ac",
    			"session_id": "d4cfc5e6-bb0f-4be7-8531-81089cb91f71",
    			"course_title": "CS 5500",
    			"answers": { "q1": "option_a" },
    			"total_scores": { "visual": 9, "auditory": 3 },
    			"status": "completed",
    			"created_at": "2024-03-01T15:42:10.000000+00:00",
    			"updated_at": null
    		}
    	],
    	"total": 1
    }
    ```
    The API returns an empty object for `answers` when no survey was completed.

### Activity Types

#### GET /api/activity-types

-   Auth: none.
-   Returns all activity types sorted by `type_name`.
-   Response snippet:
    ```json
    [
    	{
    		"type_name": "mindfulness",
    		"description": "Short grounding and breathing activities.",
    		"required_fields": ["duration_minutes", "script"],
    		"optional_fields": ["materials"],
    		"example_content_json": { "duration_minutes": 5, "script": "..." },
    		"created_at": "2024-02-01T12:00:00+00:00",
    		"updated_at": "2024-02-01T12:00:00+00:00"
    	}
    ]
    ```

#### POST /api/activity-types

-   Auth: teacher bearer token.
-   Request body:
    ```json
    {
    	"type_name": "gallery_walk",
    	"description": "Students rotate through stations adding ideas.",
    	"required_fields": ["stations", "timing"],
    	"optional_fields": ["materials", "debrief_questions"],
    	"example_content_json": {
    		"stations": [
    			{
    				"title": "Brainstorm",
    				"prompt": "Add one idea per sticky note."
    			}
    		],
    		"timing": "15 minutes"
    	}
    }
    ```
-   Response 201 echoes the persisted object.
-   Failure codes: `400 ACTIVITY_TYPE_EXISTS`.

### Activities

#### GET /api/activities

-   Auth: none.
-   Query parameters:
    -   `type` (alias for `type_filter`) filters by `Activity.type`.
    -   `tag` (single string) filters activities whose `tags` array contains the value.
-   Response 200 is a list of `ActivityOut` objects:
    ```json
    [
    	{
    		"id": "6cf18022-596c-428d-8b44-3bb994e593f3",
    		"name": "Box Breathing",
    		"summary": "Guided 4-4-4-4 breathing pattern.",
    		"type": "mindfulness",
    		"tags": ["calm", "focus"],
    		"content_json": { "duration_minutes": 5, "script": "..." },
    		"creator_id": "b6d3c9bf-d733-4ff1-a5aa-5d232a21eb2d",
    		"creator_name": "Prof. Ada Lovelace",
    		"creator_email": "prof@example.edu",
    		"created_at": "2024-02-20T17:10:00+00:00",
    		"updated_at": "2024-02-20T17:10:00+00:00"
    	}
    ]
    ```

#### GET /api/activities/{activity_id}

-   Auth: none.
-   Returns a single `ActivityOut`.
-   Failure codes: `404 ACTIVITY_NOT_FOUND`.

#### POST /api/activities

-   Auth: teacher bearer token.
-   Request body:
    ```json
    {
    	"name": "Five Senses Check-In",
    	"summary": "Students share one thing they can see, hear, and feel.",
    	"type": "mindfulness",
    	"tags": ["grounding", "community"],
    	"content_json": {
    		"duration_minutes": 10,
    		"instructions": [
    			"Prompt students for sight, sound, and touch observations."
    		]
    	}
    }
    ```
-   Response 201 returns the full `ActivityOut`.
-   Failure codes:
    -   `404 ACTIVITY_TYPE_NOT_FOUND` when `type` is unknown.
    -   `400 CONTENT_JSON_MUST_BE_OBJECT` if `content_json` is not a JSON object.
    -   `400 MISSING_REQUIRED_FIELDS` with a `fields` array listing omissions.

#### PATCH /api/activities/{activity_id}

-   Auth: teacher bearer token; only the creator can modify an activity.
-   Any subset of `name`, `summary`, `tags`, or `content_json` may be provided.
-   Response 200 mirrors `ActivityOut`.
-   Failure codes: `404 ACTIVITY_NOT_FOUND`, `403 NOT_ACTIVITY_CREATOR`, plus the same validation guards used on creation. If the stored activity type was deleted, the API raises `500 ACTIVITY_TYPE_MISSING`.

### Courses

#### POST /api/courses

-   Auth: teacher bearer token.
-   Request body:
    ```json
    {
    	"title": "Intro to Human-Centered Design",
    	"baseline_survey_id": "c51a1d83-0c8c-4cc3-a3f9-151ad5fb5f09",
    	"mood_labels": ["energized", "curious", "tired"]
    }
    ```
-   Behavior: fetches the survey template to derive `learning_style_categories`; `mood_labels` are trimmed and deduplicated; blank values are rejected.
-   Response 201:
    ```json
    {
    	"id": "ad6a32d2-6861-4fb2-9bf3-31f3ad8ac878",
    	"title": "Intro to Human-Centered Design",
    	"baseline_survey_id": "c51a1d83-0c8c-4cc3-a3f9-151ad5fb5f09",
    	"learning_style_categories": ["auditory", "kinesthetic", "visual"],
    	"mood_labels": ["energized", "curious", "tired"],
    	"requires_rebaseline": true,
    	"created_at": "2024-03-05T14:00:00+00:00",
    	"updated_at": "2024-03-05T14:00:00+00:00"
    }
    ```
-   Failure codes: `404 SURVEY_TEMPLATE_NOT_FOUND`, `400 MOOD_LABELS_REQUIRED`, `400 COURSE_TITLE_EXISTS`.

#### GET /api/courses

-   Auth: teacher bearer token.
-   Returns all courses owned by the teacher.

#### GET /api/courses/{course_id}

-   Auth: teacher bearer token.
-   Enforces ownership; otherwise returns `403 COURSE_ACCESS_DENIED`.
-   Failure codes: `404 COURSE_NOT_FOUND`.

#### PATCH /api/courses/{course_id}

-   Auth: teacher bearer token.
-   Request body accepts `title` and/or `baseline_survey_id`. Updating the baseline survey recalculates `learning_style_categories` and marks `requires_rebaseline` as `true`.
-   Response 200 mirrors `CourseOut`.
-   Failure codes mirror creation (including `SURVEY_TEMPLATE_NOT_FOUND`).

#### GET /api/courses/{course_id}/recommendations

-   Auth: teacher bearer token.
-   Returns:
    ```json
    {
    	"course_id": "ad6a32d2-6861-4fb2-9bf3-31f3ad8ac878",
    	"learning_style_categories": ["auditory", "kinesthetic", "visual"],
    	"mood_labels": ["energized", "curious", "tired"],
    	"mappings": [
    		{
    			"learning_style": "visual",
    			"mood": "curious",
    			"activity": {
    				"activity_id": "6cf18022-596c-428d-8b44-3bb994e593f3",
    				"name": "Box Breathing",
    				"summary": "Guided 4-4-4-4 breathing pattern.",
    				"type": "mindfulness",
    				"content_json": { "duration_minutes": 5, "script": "..." }
    			}
    		}
    	]
    }
    ```

#### PATCH /api/courses/{course_id}/recommendations

-   Auth: teacher bearer token.
-   Request body:
    ```json
    {
    	"mappings": [
    		{
    			"learning_style": "visual",
    			"mood": "curious",
    			"activity_id": "6cf18022-596c-428d-8b44-3bb994e593f3"
    		},
    		{
    			"learning_style": null,
    			"mood": "tired",
    			"activity_id": "30b65c54-8aba-4ba7-9f38-3a1e0a6d9e38"
    		}
    	]
    }
    ```
-   Behavior: blank or wildcard values (`null`, "\*", "any", "default") are stored as fallbacks. Entries are upserted; existing mappings are updated in place.
-   Response 200 returns the refreshed mapping set.
-   Failure codes: `400 UNKNOWN_LEARNING_STYLE:<value>`, `400 UNKNOWN_MOOD:<value>`, `404 ACTIVITY_NOT_FOUND:<id>`.

#### Recommendation Auto-Fallbacks

-   System-generated rows are tracked with `course_recommendations.is_auto`. Any teacher edit flips the flag to `false`, which shields that mapping from future auto-overwrites.
-   Immediately after course creation the backend ensures a course-global default `(learning_style=null, mood=null)` that targets the current **system default activity**. If the activity catalog is empty, the insert is deferred until activities exist.
-   After each recommendation PATCH the backend applies the teacher’s precise mappings and then auto-upserts:
    -   `(null, moodY)` so guests without a stored style still land on the latest activity for that mood.
    -   `(styleX, null)` so profile-only matches inherit the freshest rule for that style.
    -   Auto rows are created or updated only when they are missing or already marked `is_auto=true`.
-   When every database fallback misses, `get_recommended_activity` now returns `match_type="system-default"` rather than an empty activity payload.
-   System default selection order: `SYSTEM_DEFAULT_ACTIVITY_ID` env var → first activity tagged `__system_default__` → newest activity overall → none (when the catalog is empty). The seed script tags **Calm Reset Routine**, and `.env.example.docker` documents the optional override knob.

### Sessions

#### GET /api/sessions/{course_id}/sessions

-   Auth: teacher bearer token.
-   Returns every session for the course ordered by `started_at` descending so the newest session is first.
-   Response 200:
    ```json
    [
    	{
    		"session_id": "c9f3b647-9ce1-4a54-9de2-5ef182d2e8e3",
    		"course_id": "ad6a32d2-6861-4fb2-9bf3-31f3ad8ac878",
    		"require_survey": true,
    		"mood_check_schema": {
    			"prompt": "How are you feeling heading into class?",
    			"options": ["energized", "curious", "tired"]
    		},
    		"survey_snapshot_json": { "survey_id": "c51a1d83-0c8-4cc3-a3f9-151ad5fb5f09" },
    		"started_at": "2024-03-06T17:30:00+00:00",
    		"closed_at": null,
    		"join_token": "4W3L6uA9gqX2Y1bK",
    		"qr_url": "http://localhost:5173/join?s=4W3L6uA9gqX2Y1bK"
    	},
    	{
    		"session_id": "1a6423c4-51f4-4f07-9f11-2db1df5a9dff",
    		"course_id": "ad6a32d2-6861-4fb2-9bf3-31f3ad8ac878",
    		"require_survey": false,
    		"mood_check_schema": {
    			"prompt": "How are you feeling today?",
    			"options": ["energized", "curious", "tired"]
    		},
    		"survey_snapshot_json": null,
    		"started_at": "2024-02-28T15:00:00+00:00",
    		"closed_at": "2024-02-28T16:15:00+00:00",
    		"join_token": "Q2xK0uN4LgWeP6s7",
    		"qr_url": "http://localhost:5173/join?s=Q2xK0uN4LgWeP6s7"
    	}
    ]
    ```
-   Failure codes: `404 COURSE_NOT_FOUND`.

#### POST /api/sessions/{course_id}/sessions

-   Auth: teacher bearer token.
-   Request body:
    ```json
    {
    	"require_survey": true,
    	"mood_prompt": "How are you feeling heading into class?"
    }
    ```
    Both fields are optional. The API still enforces surveys when `course.requires_rebaseline` is true, and it falls back to `"How are you feeling today?"` when `mood_prompt` is missing or blank.
-   Response 201:
    ```json
    {
    	"session_id": "c9f3b647-9ce1-4a54-9de2-5ef182d2e8e3",
    	"course_id": "ad6a32d2-6861-4fb2-9bf3-31f3ad8ac878",
    	"require_survey": true,
    	"mood_check_schema": {
    		"prompt": "How are you feeling heading into class?",
    		"options": ["energized", "curious", "tired"]
    	},
    	"survey_snapshot_json": {
    		"survey_id": "c51a1d83-0c8c-4cc3-a3f9-151ad5fb5f09",
    		"title": "Baseline Learning Preferences",
    		"questions": [
    			{
    				"id": "q1",
    				"text": "How do you prefer to learn new concepts?",
    				"options": [
    					{
    						"label": "Watch a demonstration",
    						"scores": { "visual": 3 }
    					},
    					{
    						"label": "Listen to an explanation",
    						"scores": { "auditory": 3 }
    					}
    				]
    			}
    		]
    	},
    	"started_at": "2024-03-06T17:30:00+00:00",
    	"closed_at": null,
    	"join_token": "4W3L6uA9gqX2Y1bK",
    	"qr_url": "http://localhost:5173/join?s=4W3L6uA9gqX2Y1bK"
    }
    ```
-   Failure codes: `404 COURSE_NOT_FOUND`, `400 COURSE_MOOD_LABELS_NOT_CONFIGURED`, `400 COURSE_BASELINE_NOT_SET`, `404 SURVEY_TEMPLATE_NOT_FOUND`.

#### POST /api/sessions/{session_id}/close

-   Auth: teacher bearer token.
-   Response 200:
    ```json
    { "status": "CLOSED" }
    ```
-   Failure codes: `404 SESSION_NOT_FOUND`, `400 SESSION_ALREADY_CLOSED`.

#### GET /api/sessions/{session_id}/submissions

-   Auth: teacher bearer token.
-   Returns submissions ordered by creation time.
-   Response 200:
    ```json
    {
    	"session_id": "c9f3b647-9ce1-4a54-9de2-5ef182d2e8e3",
    	"count": 2,
    	"items": [
    		{
    			"student_name": null,
    			"student_id": "e54e9f57-4df1-4468-9f7f-0b6a3cb3fc7e",
    			"student_full_name": "Jordan Student",
    			"mood": "energized",
    			"answers": { "q1": "option_a" },
    			"total_scores": { "visual": 9, "auditory": 3 },
    			"learning_style": "visual",
    			"is_baseline_update": true,
    			"status": "completed",
    			"created_at": "2024-03-06T17:35:00+00:00",
    			"updated_at": "2024-03-06T17:36:00+00:00"
    		}
    	]
    }
    ```

#### GET /api/sessions/{session_id}/dashboard

-   Auth: teacher bearer token.
-   Response 200 summarises session engagement:
    ```json
    {
    	"session_id": "c9f3b647-9ce1-4a54-9de2-5ef182d2e8e3",
    	"course_id": "ad6a32d2-6861-4fb2-9bf3-31f3ad8ac878",
    	"course_title": "Intro to Human-Centered Design",
    	"require_survey": true,
    	"mood_summary": { "energized": 3, "tired": 1 },
    	"participants": [
    		{
    			"display_name": "Jordan Student",
    			"mode": "student",
    			"student_id": "e54e9f57-4df1-4468-9f7f-0b6a3cb3fc7e",
    			"guest_id": null,
    			"mood": "energized",
    			"learning_style": "visual",
    			"recommended_activity": {
    				"match_type": "style+mood",
    				"learning_style": "visual",
    				"mood": "energized",
    				"activity": {
    					"activity_id": "6cf18022-596c-428d-8b44-3bb994e593f3",
    					"name": "Box Breathing",
    					"summary": "Guided 4-4-4-4 breathing pattern.",
    					"type": "mindfulness",
    					"content_json": {
    						"duration_minutes": 5,
    						"script": "..."
    					}
    				}
    			}
    		}
    	]
    }
    ```
    The recommendation resolver falls back through style defaults, mood defaults, random course activities, and finally the platform-wide system default.

### Surveys

#### POST /api/surveys

-   Auth: teacher bearer token.
-   Request body:
    ```json
    {
    	"title": "Baseline Learning Preferences",
    	"questions": [
    		{
    			"id": "q1",
    			"text": "How do you prefer to learn new concepts?",
    			"options": [
    				{
    					"label": "Watch a demonstration",
    					"scores": { "visual": 3, "kinesthetic": 1 }
    				},
    				{
    					"label": "Listen to an explanation",
    					"scores": { "auditory": 3 }
    				}
    			]
    		}
    	]
    }
    ```
    Each question must be an object with `id`, `text`, and a non-empty `options` array. Every option must include `label` and `scores` (map of category names to numeric weights).
-   Response 200:
    ```json
    {
    	"id": "c51a1d83-0c8c-4cc3-a3f9-151ad5fb5f09",
    	"title": "Baseline Learning Preferences",
    	"questions": [
    		{
    			"id": "q1",
    			"text": "How do you prefer to learn new concepts?",
    			"options": [
    				{
    					"label": "Watch a demonstration",
    					"scores": { "visual": 3, "kinesthetic": 1 }
    				},
    				{
    					"label": "Listen to an explanation",
    					"scores": { "auditory": 3 }
    				}
    			]
    		}
    	],
    	"creator_name": "Prof. Ada Lovelace",
    	"creator_id": "b6d3c9bf-d733-4ff1-a5aa-5d232a21eb2d",
    	"creator_email": "prof@example.edu",
    	"created_at": "2024-02-28T16:00:00+00:00",
    	"total": 1
    }
    ```
-   Failure codes: detailed validation messages (e.g., "Question 1 must have an 'id' field"), plus `400 Survey with this title already exists`.

#### GET /api/surveys

-   Auth: teacher bearer token.
-   Returns all templates sorted by newest first. Each entry mirrors `SurveyTemplateOut`.

#### GET /api/surveys/{survey_id}

-   Auth: teacher bearer token.
-   Failure codes: `404 Survey template not found`.

### Public Session Flow

These endpoints serve the join-link experience. Authentication is optional; if a valid student token is supplied, submissions are tied to that student instead of guest mode.

#### GET /api/public/join/{join_token}

-   Returns session metadata when the session is open:
    ```json
    {
    	"session_id": "c9f3b647-9ce1-4a54-9de2-5ef182d2e8e3",
    	"course_id": "ad6a32d2-6861-4fb2-9bf3-31f3ad8ac878",
    	"course_title": "Intro to Human-Centered Design",
    	"require_survey": true,
    	"mood_check_schema": {
    		"prompt": "How are you feeling today?",
    		"options": ["energized", "curious", "tired"]
    	},
    	"survey": {
    		"survey_id": "c51a1d83-0c8c-4cc3-a3f9-151ad5fb5f09",
    		"title": "Baseline Learning Preferences",
    		"questions": [
    			{
    				"question_id": "q1",
    				"text": "How do you prefer to learn new concepts?",
    				"options": [
    					{
    						"option_id": "q1_opt_0",
    						"text": "Watch a demonstration"
    					},
    					{
    						"option_id": "q1_opt_1",
    						"text": "Listen to an explanation"
    					}
    				]
    			}
    		]
    	},
    	"status": "OPEN"
    }
    ```
-   Failure codes: `404 SESSION_NOT_FOUND`, `400 SESSION_CLOSED`.

#### POST /api/public/join/{join_token}/submit

-   Accepts mood check (and optional survey answers). If no bearer token is supplied or `is_guest` is true, `student_name` must be provided and the API will either reuse the supplied `guest_id` or generate one.
-   Request body (guest example):
    ```json
    {
    	"mood": "energized",
    	"answers": { "q1": "q1_opt_0" },
    	"is_guest": true,
    	"student_name": "Alex Guest",
    	"guest_id": null
    }
    ```
-   Response 200:
    ```json
    {
    	"submission_id": "1f85d7a4-5cd9-4a24-9e5c-32a1f0922a5b",
    	"student_id": null,
    	"guest_id": "0a9c8f44-6e16-4d9f-912b-e3abc96d2f5d",
    	"require_survey": true,
    	"is_baseline_update": true,
    	"mood": "energized",
    	"learning_style": "visual",
    	"total_scores": { "visual": 9, "auditory": 3 },
    	"recommended_activity": {
    		"match_type": "style+mood",
    		"learning_style": "visual",
    		"mood": "energized",
    		"activity": {
    			"activity_id": "6cf18022-596c-428d-8b44-3bb994e593f3",
    			"name": "Box Breathing",
    			"summary": "Guided 4-4-4-4 breathing pattern.",
    			"type": "mindfulness",
    			"content_json": { "duration_minutes": 5, "script": "..." }
    		}
    	},
    	"message": "Thanks! Your style for this course has been updated."
    }
    ```
-   Failure codes: `404 SESSION_NOT_FOUND`, `400 SESSION_CLOSED`, `400 INVALID_MOOD_LABEL`, `400 GUEST_NAME_REQUIRED`, `400 ANSWERS_REQUIRED`.

#### GET /api/public/join/{join_token}/submission

-   Query parameters: `guest_id` when continuing as the same guest; alternatively supply a student bearer token.
-   Response 200:
    ```json
    { "submitted": true }
    ```

### Admin Maintenance

These routes are meant for local development and automated tests.

#### POST /api/admin/reset

-   Auth: none (password gate only).
-   Request body:
    ```json
    { "password": "changeme" }
    ```
-   Response 200:
    ```json
    {
    	"deleted": {
    		"activities": 12,
    		"course_recommendations": 18,
    		"sessions": 4,
    		"students": 0
    	}
    }
    ```
-   Failure codes: `403 ADMIN_DISABLED`, `500 ADMIN_PASSWORD_NOT_CONFIGURED`, `403 INVALID_PASSWORD`.

#### POST /api/admin/seed

-   Auth: none (password gate only).
-   Request body:
    ```json
    {
        "password": "changeme",
        "seed_variant": "seed"
    }
    ```
    -   `seed_variant` (optional) chooses the script: `"seed"` (default, loads full demo data) or `"seed_deploy_test"` (loads the lightweight deploy-test dataset).
-   Response 202:
    ```json
    { "status": "seeded" }
    ```
-   Failure codes match `/api/admin/reset`.

## Database Schema Reference

### teachers

| Column        | Type            | Notes                                                       |
| ------------- | --------------- | ----------------------------------------------------------- |
| `id`          | UUID (text)     | Primary key generated with `uuid4()`.                       |
| `email`       | VARCHAR(255)    | Unique + indexed.                                           |
| `password_hash` | VARCHAR(255) | BCrypt hash produced by `hash_password()`.                  |
| `full_name`   | VARCHAR(255)    | Nullable for legacy records.                                |
| `created_at`  | TIMESTAMPTZ     | Defaults to `now()`.                                        |

- Relationships: `courses` (one-to-many), `activities` (one-to-many).

### students

| Column        | Type         | Notes                                                       |
| ------------- | ------------ | ----------------------------------------------------------- |
| `id`          | UUID (text)  | Primary key generated with `uuid4()`.                       |
| `email`       | VARCHAR(255) | Unique + indexed.                                           |
| `password_hash` | VARCHAR(255) | BCrypt hash.                                            |
| `full_name`   | VARCHAR(255) | Required.                                                   |
| `created_at`  | TIMESTAMPTZ  | Defaults to `now()`.                                        |

- Relationships: `submissions` (one-to-many), `course_profiles` (one-to-many).

### activity_types

| Column                | Type         | Notes                                             |
| --------------------- | ------------ | ------------------------------------------------- |
| `type_name`           | VARCHAR(100) | Primary key.                                      |
| `description`         | VARCHAR(1024)| Required human-readable description.              |
| `required_fields`     | JSON         | Array of field identifiers that must be supplied. |
| `optional_fields`     | JSON         | Array of optional field identifiers.              |
| `example_content_json`| JSON         | Sample payload structure (nullable).              |
| `created_at`          | TIMESTAMPTZ  | Defaults to `now()`.                              |
| `updated_at`          | TIMESTAMPTZ  | Auto-updated on change.                           |

- Relationships: `activities` (one-to-many).

### activities

| Column         | Type         | Notes                                                                 |
| -------------- | ------------ | --------------------------------------------------------------------- |
| `id`           | UUID (text)  | Primary key generated with `uuid4()`.                                 |
| `name`         | VARCHAR(255) | Activity display name.                                                |
| `summary`      | VARCHAR(1024)| Short description for catalog views.                                  |
| `type`         | VARCHAR(100) | FK → `activity_types.type_name` (`RESTRICT` on delete).               |
| `tags`         | JSON         | String array used for filtering.                                      |
| `content_json` | JSON         | Author-supplied payload honoring the activity type schema.            |
| `creator_id`   | UUID (text)  | Nullable FK → `teachers.id` (`SET NULL`).                             |
| `creator_name` | VARCHAR(255) | Stored snapshot of the author’s name.                                 |
| `creator_email`| VARCHAR(255) | Stored snapshot of the author’s email.                                |
| `created_at`   | TIMESTAMPTZ  | Defaults to `now()`.                                                  |
| `updated_at`   | TIMESTAMPTZ  | Auto-updated on change.                                               |

- Relationships: `activity_type` (many-to-one), `creator` (many-to-one), `recommendations` (one-to-many cascade delete).

### surveys (survey_template)

| Column         | Type         | Notes                                                                  |
| -------------- | ------------ | ---------------------------------------------------------------------- |
| `id`           | UUID (text)  | Primary key generated with `uuid4()`.                                  |
| `title`        | VARCHAR(255) | Unique + indexed survey title.                                         |
| `questions_json` | JSON      | Array of question objects persisted as authored.                        |
| `creator_name` | VARCHAR(255) | Stored display name of the author.                                     |
| `creator_id`   | UUID (text)  | Nullable FK → `teachers.id` (`CASCADE`).                               |
| `creator_email`| VARCHAR(255) | Optional email snapshot.                                               |
| `created_at`   | TIMESTAMPTZ  | Defaults to `now()`.                                                   |

- Relationships: `sessions` (one-to-many), `creator` (`Teacher` via `creator_id`).

### courses

| Column                    | Type         | Notes                                                                                 |
| ------------------------- | ------------ | ------------------------------------------------------------------------------------- |
| `id`                      | UUID (text)  | Primary key generated with `uuid4()`.                                                 |
| `title`                   | VARCHAR(255) | Teacher-scoped course title.                                                          |
| `teacher_id`              | UUID (text)  | FK → `teachers.id` (`CASCADE`).                                                       |
| `baseline_survey_id`      | UUID (text)  | Nullable FK → `surveys.id` (`SET NULL`).                                              |
| `learning_style_categories` | JSON      | Cached list of categories extracted from the baseline survey.                         |
| `mood_labels`             | JSON         | Course-specific mood options displayed to participants.                               |
| `requires_rebaseline`     | BOOLEAN      | Flag forcing the next session to include the baseline survey.                         |
| `created_at`              | TIMESTAMPTZ  | Defaults to `now()`.                                                                  |
| `updated_at`              | TIMESTAMPTZ  | Auto-updated on change.                                                               |

- Constraints: `Unique(teacher_id, title)` ensures course titles are unique per teacher; `Index(ix_course_teacher_id)` accelerates teacher lookups.
- Relationships: `teacher`, `sessions`, `recommendations`, `student_profiles`.

### sessions (class_session)

| Column               | Type         | Notes                                                                            |
| -------------------- | ------------ | -------------------------------------------------------------------------------- |
| `id`                 | UUID (text)  | Primary key generated with `uuid4()`.                                            |
| `course_id`          | UUID (text)  | FK → `courses.id` (`CASCADE`).                                                   |
| `survey_template_id` | UUID (text)  | Nullable FK → `surveys.id` (`RESTRICT`).                                         |
| `require_survey`     | BOOLEAN      | Whether the session enforces the baseline survey.                                |
| `mood_check_schema`  | JSON         | Prompt + options displayed to participants.                                      |
| `survey_snapshot_json` | JSON       | Immutable snapshot of the survey used during the session.                        |
| `started_at`         | TIMESTAMPTZ  | Defaults to `now()`.                                                             |
| `closed_at`          | TIMESTAMPTZ  | Null until `/close` is called.                                                   |
| `join_token`         | VARCHAR(16)  | Unique join token used by the mobile/web join flow.                              |

- Relationships: `course`, `survey_template`, `submissions`.

### submissions

| Column             | Type         | Notes                                                                                              |
| ------------------ | ------------ | -------------------------------------------------------------------------------------------------- |
| `id`               | UUID (text)  | Primary key generated with `uuid4()`.                                                              |
| `session_id`       | UUID (text)  | FK → `sessions.id` (`CASCADE`).                                                                     |
| `course_id`        | UUID (text)  | FK → `courses.id` (`CASCADE`).                                                                      |
| `student_id`       | UUID (text)  | Nullable FK → `students.id` (`CASCADE`).                                                           |
| `guest_name`       | VARCHAR(255) | Required when `student_id` is null.                                                                |
| `guest_id`         | UUID (text)  | Required when `student_id` is null (stable guest identifier).                                      |
| `mood`             | VARCHAR(50)  | Mood option selected by the participant.                                                           |
| `answers_json`     | JSON         | Optional answers keyed by question id.                                                             |
| `total_scores`     | JSON         | Optional aggregate learning style scores.                                                          |
| `is_baseline_update` | BOOLEAN    | True when the submission captured a new learning style profile.                                    |
| `status`           | VARCHAR(20)  | `"completed"` or `"skipped"` (currently always `"completed"`).                                     |
| `created_at`       | TIMESTAMPTZ  | Defaults to `now()`.                                                                               |
| `updated_at`       | TIMESTAMPTZ  | Auto-updated on change.                                                                            |

- Constraints: `Check(ck_submission_student_or_guest)` enforces exactly one of `(student_id)` or `(guest_name, guest_id)`; `Unique(session_id, student_id)` and `Unique(session_id, guest_id)` prevent duplicate submissions per participant.
- Relationships: `session`, `course`, `student`.

### course_student_profiles

| Column                | Type         | Notes                                                                                 |
| --------------------- | ------------ | ------------------------------------------------------------------------------------- |
| `id`                  | UUID (text)  | Primary key generated with `uuid4()`.                                                 |
| `course_id`           | UUID (text)  | FK → `courses.id` (`CASCADE`).                                                        |
| `student_id`          | UUID (text)  | Nullable FK → `students.id` (`CASCADE`).                                              |
| `guest_id`            | UUID (text)  | Nullable guest identifier (paired with `student_id` being null).                      |
| `latest_submission_id` | UUID (text)| Nullable FK → `submissions.id` (`SET NULL`).                                          |
| `profile_category`    | VARCHAR(100) | Current learning style label.                                                         |
| `profile_scores_json` | JSON         | Persisted aggregate scores used to derive the profile.                                |
| `first_captured_at`   | TIMESTAMPTZ  | Defaults to `now()`.                                                                  |
| `updated_at`          | TIMESTAMPTZ  | Auto-updated on change.                                                               |
| `is_current`          | BOOLEAN      | True when the row represents the active profile for the participant.                  |

- Constraints: `Unique(course_id, student_id, is_current)` and `Unique(course_id, guest_id, is_current)` guarantee only one current profile per participant per course.
- Relationships: `course`, `student`, `latest_submission`.

### course_recommendations

| Column         | Type         | Notes                                                                                     |
| -------------- | ------------ | ----------------------------------------------------------------------------------------- |
| `id`           | UUID (text)  | Primary key generated with `uuid4()`.                                                     |
| `course_id`    | UUID (text)  | FK → `courses.id` (`CASCADE`).                                                            |
| `learning_style` | VARCHAR(100) | Nullable learning style filter (treats null/empty as wildcard).                       |
| `mood`         | VARCHAR(100) | Nullable mood filter (null/empty = wildcard).                                             |
| `activity_id`  | UUID (text)  | FK → `activities.id` (`CASCADE`).                                                         |
| `is_auto`      | BOOLEAN      | True when system-generated default; manual entries remain `false`.                        |
| `created_at`   | TIMESTAMPTZ  | Defaults to `now()`.                                                                      |
| `updated_at`   | TIMESTAMPTZ  | Auto-updated on change.                                                                   |

- Constraints: `Unique(course_id, learning_style, mood)` ensures each (style, mood) combination maps to a single activity; `Index(ix_course_recommendations_course)` supports lookups by course.
- Relationships: `course`, `activity`.

Refer to `alembic/versions/` for migration history and DDL definitions.

## Seeding & Data Utilities

Scripts live in `scripts/` and are documented in `scripts/README.md`.

Quick summary:

| Command           | Description                                                                                                                         |
| ----------------- | ----------------------------------------------------------------------------------------------------------------------------------- |
| `make db-migrate`          | Run Alembic migrations (executes inside container when available).                                                           |
| `make db-seed [script.py]` | Clean + seed the DB (defaults to `scripts/seed.py`; pass `seed_deploy_test.py` for the catalog-only dataset).              |
| `make db-clean`            | Truncate every application table (metadata-driven, preserves schema).                                                       |
| `make db-status`           | Display record counts across all application tables.                                                                        |

The default seed script (`scripts/seed.py`) is idempotent: rerunning it skips existing activity
types, activities, and recommendations, updating only what is missing. The catalog-only variant
(`scripts/seed_deploy_test.py`) uses the same guards while inserting just the shared survey and
activity catalog assets.

## Development Workflow

1. **Spin up services & migrate**

    ```bash
    make dev              # starts postgres, applies migrations, seeds, runs backend
    # or run manually:
    docker compose -f docker-compose.dev.yml up -d database
    make db-migrate
    make db-seed              # cleans + seeds using scripts/seed.py
    # or keep only surveys + activity catalog:
    make db-seed seed_deploy_test.py
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

-   `app/services/surveys.py` – derive learning-style categories, compute total scores, reshape survey
    snapshots for the public API.
-   `app/services/recommendations.py` – implements the fallback chain for matching activities and
    builds response payloads.
-   `app/services/submissions.py` – single upsert path for submissions, plus management of
    `course_student_profiles` when a baseline is updated.

Unit tests for these helpers live in `tests/test_services.py` and run entirely against an
in-memory SQLite database (no external dependencies).

## Testing Quickstart

1. Ensure services are up: `make dev`.
2. Run `make test` (or `uv run pytest tests/ -v`).
3. For ad-hoc smoke checks without a DB: `uv run pytest tests/test_api.py::test_health_and_auth_guards`.

The integration tests will automatically skip database-marked tests if the connection fails.

## Admin Notes

All authenticated teachers can now create activity types; no additional configuration is required.

-   Dev/test builds expose two maintenance endpoints for local setup:
    -   `POST /api/admin/reset` clears every table but keeps the schema. Request body: `{"password": "<value>"}`.
    -   `POST /api/admin/seed` runs `scripts/seed.py` to repopulate demo data.
    -   Both routes require `MAINTENANCE_ADMIN_PASSWORD` to be set (see `.env.example.docker`) and are disabled when `APP_ENV` is not `dev` or `test`.

## Contributing Tips

-   When adding new endpoints, include schemas in `app/schemas/` and add matching tests.
-   All changes that touch the database must include an Alembic migration.
-   Keep seed data idempotent; tests rely on being able to reseed without duplicates.
-   Prefer service helpers in `app/services/` for complex logic; unit test them in isolation.

Enjoy building productive classrooms!
