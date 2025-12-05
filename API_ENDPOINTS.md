# API paths the frontend should call

All paths below are the exact route strings registered in `app/main.py` (router prefix + route decorator path). Include the trailing slash when shown. Endpoints tagged "Teacher auth" or "Student auth" require an `Authorization: Bearer <access_token>` header from the corresponding login route.

## Base
- `GET /` – sanity check.
- `GET /health` – health probe.

## Teacher authentication (`/api/teachers`)
- `POST /api/teachers/signup`
- `POST /api/teachers/login`

## Student authentication (`/api/students`)
- `POST /api/students/signup`
- `POST /api/students/login`
- `GET  /api/students/me` (Student auth)
- `GET  /api/students/submissions` (Student auth)

## Activity types (`/api/activity-types`)
- `GET  /api/activity-types/`
- `POST /api/activity-types/` (Teacher auth)

## Activities (`/api/activities`)
- `GET  /api/activities/?tag=<tag>&type=<type>` – query params optional.
- `GET  /api/activities/{activity_id}`
- `POST /api/activities/` (Teacher auth)
- `PATCH /api/activities/{activity_id}` (Teacher auth; creator-only)

## Courses (`/api/courses`)
- `POST   /api/courses/` (Teacher auth)
- `GET    /api/courses/` (Teacher auth)
- `GET    /api/courses/{course_id}` (Teacher auth)
- `PATCH  /api/courses/{course_id}` (Teacher auth)
- `DELETE /api/courses/{course_id}` (Teacher auth)
- `GET    /api/courses/{course_id}/recommendations` (Teacher auth)
- `PATCH  /api/courses/{course_id}/recommendations` (Teacher auth)
- `POST   /api/courses/{course_id}/recommendations/auto` (Teacher auth; generates AI suggestions, does not persist)

## Sessions (`/api/sessions`)
- `GET  /api/sessions/{course_id}/sessions` (Teacher auth; list sessions for a course)
- `POST /api/sessions/{course_id}/sessions` (Teacher auth; create session for a course)
- `POST /api/sessions/{session_id}/close` (Teacher auth)
- `GET  /api/sessions/{session_id}/submissions` (Teacher auth)
- `GET  /api/sessions/{session_id}/dashboard` (Teacher auth)

## Surveys (`/api/surveys`)
- `POST /api/surveys/` (Teacher auth)
- `GET  /api/surveys/` (Teacher auth)
- `GET  /api/surveys/{survey_id}` (Teacher auth)

## Public join + submit (`/api/public`)
- `GET  /api/public/join/{join_token}`
- `POST /api/public/join/{join_token}/submit` – accepts optional student auth; guest mode allowed.
- `GET  /api/public/join/{join_token}/submission?guest_id=<id>` – optional `guest_id`; student auth also works.

## Admin tools (`/api/admin`) — dev/test only, password-protected
- `POST /api/admin/reset`
- `POST /api/admin/seed`
