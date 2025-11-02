# Postman Manual Testing Guide

This guide explains how to exercise **every API endpoint** in the CS5500 classroom engagement backend with Postman. Follow the sequence to mimic real classroom flows (teacher setup → course + content → live session → public submissions) and to capture edge cases.

---

## Prerequisites
- Backend running locally (default `http://localhost:8000`) with a reachable PostgreSQL database.
- Schema migrated and (optionally) seeded: `make db-migrate && make db-seed`.
- Your teacher email appears in `ADMIN_EMAILS` so you may create activity types. (Edit `.env` or export `ADMIN_EMAILS=teacher@example.com` before starting the server.)
- Postman desktop/app installed.

---

## Sample Data Used in Examples
The request bodies below use the following fake but realistic data. Replace values with your own as needed.

| Field | Sample Value |
|-------|--------------|
| Base URL | `http://localhost:8000` |
| Teacher email/password | `michaeltest@example.com` / `Password123!` |
| Teacher full name | `Michael Test` |
| Student email/password | `sarahstudent@example.com` / `StudentPass123!` |
| Student full name | `Sarah Student` |
| Survey ID | `11111111-2222-3333-4444-555555555555` |
| Course ID | `aaaaaaaa-bbbb-cccc-dddd-eeeeeeeeeeee` |
| Activity type name | `breathing-routine-demo` |
| Activity ID | `99999999-8888-7777-6666-555555555555` |
| Session ID | `12345678-90ab-cdef-1234-567890abcdef` |
| Join token | `joinTokenSample123` |
| Guest ID | `guest-sample-12345` |

> Tip: After each successful request, capture the real IDs/tokens returned by your server and reuse them in later calls.

---

## Suggested Postman Collection Layout
```
CS5500 Backend
├─ 00 Diagnostics (/, /health)
├─ 01 Teacher Auth
├─ 02 Student Auth
├─ 03 Surveys
├─ 04 Courses
├─ 05 Activity Types
├─ 06 Activities
├─ 07 Course Recommendations
├─ 08 Sessions (Teacher)
├─ 09 Public Join & Submission
└─ 10 Student History
```

---

## Step-by-Step Testing Flow

### 0. Diagnostics (No Auth)
1. **GET** `http://localhost:8000/`  
   - Expect `200` with `{"message": "5500 Backend is running!"}`.
2. **GET** `http://localhost:8000/health`  
   - Expect `200` with JSON containing `"status": "ok"` and current environment.

### 1. Teacher Authentication
3. **POST** `http://localhost:8000/api/teachers/signup`  
   Body (`raw/json`):
   ```json
   {
     "email": "michaeltest@example.com",
     "password": "Password123!",
     "full_name": "Test Teacher"
   }
   ```
   - Expect `200`. **Tests tab**:
   ```js
   pm.environment.set("teacherEmail", pm.request.body.toJSON().email);
   ```
   - Optional negative: resubmit same email → expect `400` with `AUTH_EMAIL_EXISTS`.

4. **POST** `http://localhost:8000/api/teachers/login`  
   Body:
   ```json
   {
     "email": "michaeltest@example.com",
     "password": "Password123!"
   }
   ```
   - Expect `200` with `access_token`. **Tests tab**:
   ```js
   pm.environment.set("teacherToken", pm.response.json().access_token);
   ```
   - Confirm `Authorization` header for teacher endpoints uses `Bearer TEACHER_JWT_TOKEN`.

5. Negative guard: **GET** `http://localhost:8000/api/courses` without `Authorization` → expect `403`.

### 2. Student Authentication
6. **POST** `http://localhost:8000/api/students/signup`  
   Body:
   ```json
   {
     "email": "sarahstudent@example.com",
     "password": "StudentPass123!",
     "full_name": "Test Student"
   }
   ```
   - Expect `200`. Save email/password if using random data.

7. **POST** `http://localhost:8000/api/students/login`  
   Body mirrors signup email/password. Save token:
   ```js
   pm.environment.set("studentToken", pm.response.json().access_token);
   ```

8. **GET** `http://localhost:8000/api/students/me` with `Authorization: Bearer STUDENT_JWT_TOKEN`  
   - Expect `200` with student profile.

9. **GET** `http://localhost:8000/api/students/submissions` with student token  
   - Expect `200` with `total: 0` initially.

### 3. Survey Templates (Teacher JWT required)
Headers: `Authorization: Bearer TEACHER_JWT_TOKEN`

10. **POST** `http://localhost:8000/api/surveys`  
    Example body:
    ```json
    {
      "title": "Baseline Survey 2024-05-01",
      "questions": [
        {
          "id": "q1",
          "text": "Preferred learning mode?",
          "options": [
            {"label": "Visual", "scores": {"Visual": 2, "Auditory": 0}},
            {"label": "Auditory", "scores": {"Visual": 0, "Auditory": 2}}
          ]
        },
        {
          "id": "q2",
          "text": "Activity preference?",
          "options": [
            {"label": "Hands-on", "scores": {"Kinesthetic": 3}},
            {"label": "Lecture", "scores": {"Auditory": 2}}
          ]
        }
      ]
    }
    ```
    - Expect `200`. Save id:
    ```js
    pm.environment.set("surveyId", pm.response.json().id);
    ```
    - Invalid payload tests: remove `options` array → expect `400`.

11. **GET** `http://localhost:8000/api/surveys`  
    - Expect list including the survey above.

12. **GET** `http://localhost:8000/api/surveys/11111111-2222-3333-4444-555555555555`  
    - Confirms retrieval of single template.

### 4. Courses (Teacher JWT)
13. **POST** `http://localhost:8000/api/courses`  
    Body:
    ```json
    {
      "title": "CS101 Section A",
      "baseline_survey_id": "11111111-2222-3333-4444-555555555555",
      "mood_labels": ["energized", "steady", "worried"]
    }
    ```
    - Expect `201` with `requires_rebaseline: true`. Save course id and mood labels:
    ```js
    const course = pm.response.json();
    pm.environment.set("courseId", course.id);
    ```

14. **GET** `http://localhost:8000/api/courses`  
    - Should list the course you just created.

15. **GET** `http://localhost:8000/api/courses/{{courseId}}`  
    - Expect `200` with the course you created. If you use a different teacher token, expect `403`.

16. **PATCH** `http://localhost:8000/api/courses/aaaaaaaa-bbbb-cccc-dddd-eeeeeeeeeeee`  
    Body (optional update):
    ```json
    {
      "title": "CS101 Section A (Updated)",
      "baseline_survey_id": "11111111-2222-3333-4444-555555555555"
    }
    ```
    - Expect `200`. Confirm `requires_rebaseline` flips to `true` when baseline changed.
    - Attempt to send `mood_labels` here → expect unchanged list (field ignored).

### 5. Activity Types (Admin Teacher JWT)
Headers: `Authorization: Bearer TEACHER_JWT_TOKEN`

17. **POST** `http://localhost:8000/api/activity-types`  
    Body:
    ```json
    {
      "type_name": "breathing-routine-demo",
      "description": "Guided calm routine",
      "required_fields": ["script_steps"],
      "optional_fields": ["duration_sec"],
      "example_content_json": {"script_steps": ["Inhale", "Hold", "Exhale"]}
    }
    ```
    - Expect `201`. Save type name:
    ```js
    pm.environment.set("activityTypeName", pm.request.body.toJSON().type_name);
    ```
    - Re-run with identical payload → expect `400` `ACTIVITY_TYPE_EXISTS`.

18. **GET** `http://localhost:8000/api/activity-types`  
    - Verify the new type appears.

### 6. Activities (Teacher JWT)
19. **POST** `http://localhost:8000/api/activities`  
    Body:
    ```json
    {
      "name": "Quick Calm Routine",
      "summary": "Simple breathing exercise",
      "type": "breathing-routine-demo",
      "tags": ["calm", "focus"],
      "content_json": {
        "script_steps": ["Inhale 4", "Hold 4", "Exhale 4"],
        "duration_sec": 60
      }
    }
    ```
    - Expect `201`. Save id:
    ```js
    pm.environment.set("activityId", pm.response.json().id);
    ```
    - Negative: omit `script_steps` → expect `400` `MISSING_REQUIRED_FIELDS`.

20. **GET** `http://localhost:8000/api/activities` (no filters)  
    - Expect array containing the new activity.

21. **GET** `http://localhost:8000/api/activities?type=breathing-routine-demo`  
    - Confirms query filter works.

22. **GET** `http://localhost:8000/api/activities/99999999-8888-7777-6666-555555555555`  
    - Expect `200` with full record.

23. **PATCH** `http://localhost:8000/api/activities/99999999-8888-7777-6666-555555555555`  
    Body:
    ```json
    {
      "summary": "Updated calm routine summary",
      "tags": ["calm", "breathing"]
    }
    ```
    - Expect `200` with updated fields.

### 7. Course Recommendations (Teacher JWT)
24. **PATCH** `http://localhost:8000/api/courses/aaaaaaaa-bbbb-cccc-dddd-eeeeeeeeeeee/recommendations`  
    Body:
    ```json
    {
      "mappings": [
        {
          "learning_style": "Visual",
          "mood": "worried",
          "activity_id": "99999999-8888-7777-6666-555555555555"
        },
        {
          "learning_style": null,
          "mood": "energized",
          "activity_id": "99999999-8888-7777-6666-555555555555"
        }
      ]
    }
    ```
    - Expect `200` with updated mappings.
    - Negative: supply `mood: "unknown"` → expect `400` `UNKNOWN_MOOD`.

25. **GET** `http://localhost:8000/api/courses/aaaaaaaa-bbbb-cccc-dddd-eeeeeeeeeeee/recommendations`  
    - Verify the mappings, mood labels, and learning-style categories.

### 8. Sessions (Teacher JWT)
26. **POST** `http://localhost:8000/api/sessions/aaaaaaaa-bbbb-cccc-dddd-eeeeeeeeeeee/sessions`  
    Body:
    ```json
    { "require_survey": false }
    ```
    - Because the course requires rebaseline, expect `require_survey: true` in response.
    - Save identifiers:
    ```js
    const data = pm.response.json();
    pm.environment.set("sessionId", data.session_id);
    pm.environment.set("joinToken", data.join_token);
    ```
    - Save QR URL if needed.

27. **GET** `http://localhost:8000/api/sessions/12345678-90ab-cdef-1234-567890abcdef/submissions`  
    - Expect `count: 0`.

28. **GET** `http://localhost:8000/api/sessions/12345678-90ab-cdef-1234-567890abcdef/dashboard`  
    - Expect empty `participants` array initially.

### 9. Public Join & Submission (No Auth / Optional Student Auth)
29. **GET** `http://localhost:8000/api/public/join/joinTokenSample123`  
    - Expect `200` with course + survey snapshot (because survey required).

30. Negative validation: **POST** `.../submit` with missing mood  
    ```json
    { "is_guest": true }
    ```
    - Expect `422`.

31. **POST** `http://localhost:8000/api/public/join/joinTokenSample123/submit` (Guest, survey required)  
    Body:
    ```json
    {
      "is_guest": true,
      "student_name": "Guest One",
      "mood": "worried",
      "answers": {
        "q1": "Visual",
        "q2": "Hands-on"
      }
    }
    ```
    - Expect `200` with `is_baseline_update: true`.
    - Save identifiers:
    ```js
    const payload = pm.response.json();
    pm.environment.set("submissionId", payload.submission_id);
    pm.environment.set("guestId", payload.guest_id);
    ```

32. Resubmit as same guest to verify idempotent upsert: include `"guest_id": "guest-sample-12345"` and change `"mood": "energized"` → expect response shares same `submission_id`.

33. **GET** `http://localhost:8000/api/public/join/joinTokenSample123/submission?guest_id=guest-sample-12345`  
    - Expect `{"submitted": true}`.

34. **GET** `http://localhost:8000/api/sessions/12345678-90ab-cdef-1234-567890abcdef/submissions` (Teacher JWT)  
    - Expect `count >= 1`, confirm mood updated.

35. **GET** `http://localhost:8000/api/sessions/12345678-90ab-cdef-1234-567890abcdef/dashboard`  
    - Expect participant entry with `recommended_activity`.

35. **POST** `http://localhost:8000/api/sessions/12345678-90ab-cdef-1234-567890abcdef/close` (Teacher JWT)  
    - Expect `{"status": "CLOSED"}`.

36. **GET** `http://localhost:8000/api/public/join/joinTokenSample123`  
    - Now returns `400` `SESSION_CLOSED`.

37. Create a second session where survey is optional: repeat step 25 and save new `sessionId`/`joinToken`. Confirm `require_survey` is `false` this time because the course no longer requires rebaseline.

38. Logged-in student submission (no survey required):  
    **POST** `http://localhost:8000/api/public/join/joinTokenSample123/submit` with header `Authorization: Bearer STUDENT_JWT_TOKEN` and body:
    ```json
    {
      "is_guest": false,
      "mood": "steady"
    }
    ```
    - Expect `200`, `is_baseline_update: false`.

39. **GET** `http://localhost:8000/api/public/join/joinTokenSample123/submission` with student token (no params) → expect `{"submitted": true}`.

40. Negative mood validation: submit with `"mood": "elated"` → expect `400` `INVALID_MOOD_LABEL`.

### 10. Student History
41. **GET** `http://localhost:8000/api/students/submissions` with `Authorization: Bearer STUDENT_JWT_TOKEN`  
    - Expect `total >= 1` and record for the session above.

### 11. Additional Auth Edge Cases
- Teacher login with wrong password → expect `401` `AUTH_INVALID_CREDENTIALS`.
- Student login wrong password → expect `401`.
- Any teacher-only endpoint without token → expect `403`.

---

## Handy Postman Tests Snippets
Use these snippets in the **Tests** tab to automate variable capture:
```javascript
// Save token (teacher or student)
if (pm.response.code === 200 && pm.response.json().access_token) {
  pm.environment.set("teacherToken", pm.response.json().access_token);
}

// Generic setter helper
const body = pm.response.json();
if (body.id) pm.environment.set("resourceId", body.id);

// Assert for expected code/message
pm.test("Status is 200", () => pm.response.code === 200);
```

---

## Cleanup Ideas
- **Close sessions** (already covered) to simulate course end.
- **Re-run submissions** with new moods to confirm dashboards refresh.
- **Create additional courses/surveys** to validate list endpoints.
- Use `DELETE` or truncation scripts if you prefer a clean DB between manual passes (`make db-clean`).

With these steps, every endpoint and primary code path is exercised within a single Postman collection run. Adjust payloads as needed for exploratory testing or regression checks.

---

## Copy-Paste Request Bodies
Use the snippets below directly in Postman's **Body → raw → JSON** field.

### Teacher Auth
```json
{
  "email": "michaeltest@example.com",
  "password": "Password123!",
  "full_name": "Test Teacher"
}
```

```json
{
  "email": "michaeltest@example.com",
  "password": "Password123!"
}
```

### Student Auth
```json
{
  "email": "sarahstudent@example.com",
  "password": "StudentPass123!",
  "full_name": "Test Student"
}
```

```json
{
  "email": "sarahstudent@example.com",
  "password": "StudentPass123!"
}
```

### Survey Template
```json
{
  "title": "Baseline Survey 2024-05-01",
  "questions": [
    {
      "id": "q1",
      "text": "Preferred learning mode?",
      "options": [
        { "label": "Visual", "scores": { "Visual": 2, "Auditory": 0 } },
        { "label": "Auditory", "scores": { "Visual": 0, "Auditory": 2 } }
      ]
    },
    {
      "id": "q2",
      "text": "Activity preference?",
      "options": [
        { "label": "Hands-on", "scores": { "Kinesthetic": 3 } },
        { "label": "Lecture", "scores": { "Auditory": 2 } }
      ]
    }
  ]
}
```

### Course Create
```json
{
  "title": "CS101 Section A",
  "baseline_survey_id": "11111111-2222-3333-4444-555555555555",
  "mood_labels": ["energized", "steady", "worried"]
}
```

### Course Update
```json
{
  "title": "CS101 Section A (Updated)",
  "baseline_survey_id": "11111111-2222-3333-4444-555555555555"
}
```

### Activity Type Create
```json
{
  "type_name": "breathing-routine-demo",
  "description": "Guided calm routine",
  "required_fields": ["script_steps"],
  "optional_fields": ["duration_sec"],
  "example_content_json": { "script_steps": ["Inhale", "Hold", "Exhale"] }
}
```

### Activity Create
```json
{
  "name": "Quick Calm Routine",
  "summary": "Simple breathing exercise",
  "type": "breathing-routine-demo",
  "tags": ["calm", "focus"],
  "content_json": {
    "script_steps": ["Inhale 4", "Hold 4", "Exhale 4"],
    "duration_sec": 60
  }
}
```

### Activity Update
```json
{
  "summary": "Updated calm routine summary",
  "tags": ["calm", "breathing"]
}
```

### Course Recommendations Upsert
```json
{
  "mappings": [
    {
      "learning_style": "Visual",
      "mood": "worried",
      "activity_id": "99999999-8888-7777-6666-555555555555"
    },
    {
      "learning_style": null,
      "mood": "energized",
      "activity_id": "99999999-8888-7777-6666-555555555555"
    }
  ]
}
```

### Session Create
```json
{
  "require_survey": false
}
```

### Public Submission (guest, survey required)
```json
{
  "is_guest": true,
  "student_name": "Guest One",
  "mood": "worried",
  "answers": {
    "q1": "Visual",
    "q2": "Hands-on"
  }
}
```

### Public Submission Update (guest recheck)
```json
{
  "is_guest": true,
  "student_name": "Guest One",
  "guest_id": "guest-sample-12345",
  "mood": "energized",
  "answers": {
    "q1": "Visual",
    "q2": "Hands-on"
  }
}
```

### Public Submission (logged-in student, no survey)
```json
{
  "is_guest": false,
  "mood": "steady"
}
```

### Invalid Mood Example
```json
{
  "is_guest": true,
  "student_name": "Guest Two",
  "mood": "elated"
}
```
