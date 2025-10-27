#!/usr/bin/env python3
"""
Seed Script aligned with current schema

Tables: teachers, courses, students, surveys, sessions, submissions
- Creates one teacher, one course
- Creates two students
- Inserts two surveys (questions_json)
- Creates two sessions for the course (each bound to a survey)
- Inserts three sample submissions (2 authenticated, 1 guest)
"""

import json
import sys
import uuid
from pathlib import Path
from typing import Any

from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker

# Adjust path to import app modules
project_root = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(project_root))

from app.core.config import settings  # noqa: E402
from app.core.security import hash_password  # noqa: E402

# -----------------------------
# DB setup (use same URL as app)
# -----------------------------
SQLALCHEMY_DATABASE_URL = settings.database_url
engine = create_engine(SQLALCHEMY_DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def calculate_sample_scores(
    answers: dict[str, str], survey_template_questions: list[dict[str, Any]]
) -> dict[str, int]:
    """Aggregate scores per category based on selected answers."""
    all_categories = set()
    for q in survey_template_questions:
        for opt in q.get("options", []):
            all_categories.update(opt.get("scores", {}).keys())
    totals = {c: 0 for c in all_categories}

    for q in survey_template_questions:
        qid = q.get("id")
        if qid not in answers:
            continue
        picked = answers[qid]
        for opt in q.get("options", []):
            if opt.get("label") == picked:
                for c, s in opt.get("scores", {}).items():
                    if c in totals:
                        totals[c] += s
                break
    return totals


def seed_data() -> None:
    """Seed the database with essential data according to the latest schema."""
    db = SessionLocal()
    try:
        print("🌱 Starting database seeding...")

        # -----------------------------
        # 1) Clear existing data (FK-safe order)
        # -----------------------------
        print("🗑️  Clearing existing data...")
        for table in ("submissions", "sessions", "courses", "surveys", "students", "teachers"):
            try:
                db.execute(text(f"DELETE FROM {table}"))
            except Exception:
                # Table might not exist on a fresh DB
                pass
        db.commit()
        print("✅ Cleared existing data")

        # -----------------------------
        # 2) Create a teacher
        # -----------------------------
        teacher_id = str(uuid.uuid4())
        teacher_email = "teacher1@example.com"
        teacher_full_name = "Dr. Smith"
        hashed_password = hash_password("Passw0rd!")

        db.execute(
            text(
                """
                INSERT INTO teachers (id, email, password_hash, full_name, created_at)
                VALUES (:id, :email, :password_hash, :full_name, now())
                """
            ),
            {
                "id": teacher_id,
                "email": teacher_email,
                "password_hash": hashed_password,
                "full_name": teacher_full_name,
            },
        )
        print(f"✅ Created teacher: {teacher_email} ({teacher_full_name})")

        # -----------------------------
        # 3) Create a course for that teacher
        # -----------------------------
        course_id = str(uuid.uuid4())
        course_title = "CS101 — Intro Class"

        db.execute(
            text(
                """
                INSERT INTO courses (id, title, teacher_id, created_at)
                VALUES (:id, :title, :teacher_id, now())
                """
            ),
            {"id": course_id, "title": course_title, "teacher_id": teacher_id},
        )
        print(f"✅ Created course: {course_title}")

        # -----------------------------
        # 4) Create students
        # -----------------------------
        print("👨‍🎓 Creating students...")

        student_1_id = str(uuid.uuid4())
        student_1_email = "student1@example.com"
        student_1_full_name = "Alex Johnson"
        student_1_password = hash_password("Passw0rd!")
        db.execute(
            text(
                """
                INSERT INTO students (id, email, password_hash, full_name, created_at)
                VALUES (:id, :email, :password_hash, :full_name, now())
                """
            ),
            {
                "id": student_1_id,
                "email": student_1_email,
                "password_hash": student_1_password,
                "full_name": student_1_full_name,
            },
        )
        print(f"✅ Created student: {student_1_email} ({student_1_full_name})")

        student_2_id = str(uuid.uuid4())
        student_2_email = "student2@example.com"
        student_2_full_name = "Maya Chen"
        student_2_password = hash_password("Passw0rd!")
        db.execute(
            text(
                """
                INSERT INTO students (id, email, password_hash, full_name, created_at)
                VALUES (:id, :email, :password_hash, :full_name, now())
                """
            ),
            {
                "id": student_2_id,
                "email": student_2_email,
                "password_hash": student_2_password,
                "full_name": student_2_full_name,
            },
        )
        print(f"✅ Created student: {student_2_email} ({student_2_full_name})")

        # -----------------------------
        # 5) Create surveys (surveys.id/title/questions_json/creator_name/created_at)
        # -----------------------------
        print("📝 Creating surveys...")

        # Survey 1: Learning Buddy: Style Check
        survey_1_id = str(uuid.uuid4())
        survey_1_title = "Learning Buddy: Style Check"
        survey_1_questions = [
            {
                "id": "q1",
                "text": "When I can move or use my hands, I learn better.",
                "options": [
                    {
                        "label": "1 — Not at all",
                        "scores": {
                            "Active learner": 1,
                            "Structured learner": 0,
                            "Passive learner": 0,
                        },
                    },
                    {
                        "label": "2 — A little",
                        "scores": {
                            "Active learner": 2,
                            "Structured learner": 0,
                            "Passive learner": 0,
                        },
                    },
                    {
                        "label": "3 — Not sure",
                        "scores": {
                            "Active learner": 3,
                            "Structured learner": 0,
                            "Passive learner": 0,
                        },
                    },
                    {
                        "label": "4 — Mostly",
                        "scores": {
                            "Active learner": 4,
                            "Structured learner": 0,
                            "Passive learner": 0,
                        },
                    },
                    {
                        "label": "5 — Yes, a lot",
                        "scores": {
                            "Active learner": 5,
                            "Structured learner": 0,
                            "Passive learner": 0,
                        },
                    },
                ],
            },
            {
                "id": "q2",
                "text": "A short move break before learning helps me.",
                "options": [
                    {
                        "label": "1 — Not at all",
                        "scores": {
                            "Active learner": 1,
                            "Structured learner": 0,
                            "Passive learner": 0,
                        },
                    },
                    {
                        "label": "2 — A little",
                        "scores": {
                            "Active learner": 2,
                            "Structured learner": 0,
                            "Passive learner": 0,
                        },
                    },
                    {
                        "label": "3 — Not sure",
                        "scores": {
                            "Active learner": 3,
                            "Structured learner": 0,
                            "Passive learner": 0,
                        },
                    },
                    {
                        "label": "4 — Mostly",
                        "scores": {
                            "Active learner": 4,
                            "Structured learner": 0,
                            "Passive learner": 0,
                        },
                    },
                    {
                        "label": "5 — Yes, a lot",
                        "scores": {
                            "Active learner": 5,
                            "Structured learner": 0,
                            "Passive learner": 0,
                        },
                    },
                ],
            },
            {
                "id": "q3",
                "text": "Pictures or step cards make things clear for me.",
                "options": [
                    {
                        "label": "1 — Not at all",
                        "scores": {
                            "Active learner": 0,
                            "Structured learner": 1,
                            "Passive learner": 0,
                        },
                    },
                    {
                        "label": "2 — A little",
                        "scores": {
                            "Active learner": 0,
                            "Structured learner": 2,
                            "Passive learner": 0,
                        },
                    },
                    {
                        "label": "3 — Not sure",
                        "scores": {
                            "Active learner": 0,
                            "Structured learner": 3,
                            "Passive learner": 0,
                        },
                    },
                    {
                        "label": "4 — Mostly",
                        "scores": {
                            "Active learner": 0,
                            "Structured learner": 4,
                            "Passive learner": 0,
                        },
                    },
                    {
                        "label": "5 — Yes, a lot",
                        "scores": {
                            "Active learner": 0,
                            "Structured learner": 5,
                            "Passive learner": 0,
                        },
                    },
                ],
            },
            {
                "id": "q4",
                "text": "A clear checklist or plan helps me focus.",
                "options": [
                    {
                        "label": "1 — Not at all",
                        "scores": {
                            "Active learner": 0,
                            "Structured learner": 1,
                            "Passive learner": 0,
                        },
                    },
                    {
                        "label": "2 — A little",
                        "scores": {
                            "Active learner": 0,
                            "Structured learner": 2,
                            "Passive learner": 0,
                        },
                    },
                    {
                        "label": "3 — Not sure",
                        "scores": {
                            "Active learner": 0,
                            "Structured learner": 3,
                            "Passive learner": 0,
                        },
                    },
                    {
                        "label": "4 — Mostly",
                        "scores": {
                            "Active learner": 0,
                            "Structured learner": 4,
                            "Passive learner": 0,
                        },
                    },
                    {
                        "label": "5 — Yes, a lot",
                        "scores": {
                            "Active learner": 0,
                            "Structured learner": 5,
                            "Passive learner": 0,
                        },
                    },
                ],
            },
            {
                "id": "q5",
                "text": "My energy right now is…",
                "options": [
                    {
                        "label": "1 — Very low",
                        "scores": {
                            "Active learner": 0,
                            "Structured learner": 0,
                            "Passive learner": 5,
                        },
                    },
                    {
                        "label": "2 — Low",
                        "scores": {
                            "Active learner": 0,
                            "Structured learner": 0,
                            "Passive learner": 4,
                        },
                    },
                    {
                        "label": "3 — Okay",
                        "scores": {
                            "Active learner": 0,
                            "Structured learner": 0,
                            "Passive learner": 3,
                        },
                    },
                    {
                        "label": "4 — High",
                        "scores": {
                            "Active learner": 0,
                            "Structured learner": 0,
                            "Passive learner": 2,
                        },
                    },
                    {
                        "label": "5 — Very high",
                        "scores": {
                            "Active learner": 0,
                            "Structured learner": 0,
                            "Passive learner": 1,
                        },
                    },
                ],
            },
            {
                "id": "q6",
                "text": "My worry right now is…",
                "options": [
                    {
                        "label": "1 — Not worried",
                        "scores": {
                            "Active learner": 0,
                            "Structured learner": 0,
                            "Passive learner": 1,
                        },
                    },
                    {
                        "label": "2 — A little worried",
                        "scores": {
                            "Active learner": 0,
                            "Structured learner": 0,
                            "Passive learner": 2,
                        },
                    },
                    {
                        "label": "3 — Somewhat worried",
                        "scores": {
                            "Active learner": 0,
                            "Structured learner": 0,
                            "Passive learner": 3,
                        },
                    },
                    {
                        "label": "4 — Quite worried",
                        "scores": {
                            "Active learner": 0,
                            "Structured learner": 0,
                            "Passive learner": 4,
                        },
                    },
                    {
                        "label": "5 — Very worried",
                        "scores": {
                            "Active learner": 0,
                            "Structured learner": 0,
                            "Passive learner": 5,
                        },
                    },
                ],
            },
            {
                "id": "q7",
                "text": "What do you want to do first?",
                "options": [
                    {
                        "label": "A —  Move break",
                        "scores": {
                            "Active learner": 5,
                            "Structured learner": 0,
                            "Passive learner": 0,
                        },
                    },
                    {
                        "label": "B — Calm time",
                        "scores": {
                            "Active learner": 0,
                            "Structured learner": 0,
                            "Passive learner": 5,
                        },
                    },
                    {
                        "label": "C — Lesson preview",
                        "scores": {
                            "Active learner": 0,
                            "Structured learner": 5,
                            "Passive learner": 0,
                        },
                    },
                ],
            },
            {
                "id": "q8",
                "text": "When I get stuck, I like to…",
                "options": [
                    {
                        "label": "A — Try it with hands/body",
                        "scores": {
                            "Active learner": 5,
                            "Structured learner": 0,
                            "Passive learner": 0,
                        },
                    },
                    {
                        "label": "B — Look at an example or steps",
                        "scores": {
                            "Active learner": 0,
                            "Structured learner": 5,
                            "Passive learner": 0,
                        },
                    },
                    {
                        "label": "C — Take a quiet minute first",
                        "scores": {
                            "Active learner": 0,
                            "Structured learner": 0,
                            "Passive learner": 5,
                        },
                    },
                ],
            },
            {
                "id": "q9",
                "text": "Which starter helps you most today?",
                "options": [
                    {
                        "label": "A — Quick game / movement challenge",
                        "scores": {
                            "Active learner": 5,
                            "Structured learner": 0,
                            "Passive learner": 0,
                        },
                    },
                    {
                        "label": "B — Picture card of today's steps",
                        "scores": {
                            "Active learner": 0,
                            "Structured learner": 5,
                            "Passive learner": 0,
                        },
                    },
                    {
                        "label": "C — Quiet breath + 30-sec video",
                        "scores": {
                            "Active learner": 0,
                            "Structured learner": 0,
                            "Passive learner": 5,
                        },
                    },
                ],
            },
        ]

        db.execute(
            text(
                """
                INSERT INTO surveys (id, title, questions_json, creator_name, created_at)
                VALUES (:id, :title, :questions_json, :creator_name, now())
                """
            ),
            {
                "id": survey_1_id,
                "title": survey_1_title,
                "questions_json": json.dumps(survey_1_questions),
                "creator_name": "system",
            },
        )
        print(f"✅ Created survey: {survey_1_title}")

        # Survey 2: Critter Quest: Learning Adventure
        survey_2_id = str(uuid.uuid4())
        survey_2_title = "Critter Quest: Learning Adventure"
        survey_2_questions = [
            {
                "id": "q1",
                "text": "On a learning playground, I like to jump in and try things first.",
                "options": [
                    {
                        "label": "1 — Not me",
                        "scores": {
                            "Active learner": 1,
                            "Structured learner": 0,
                            "Passive learner": 0,
                            "Buddy/Social learner": 0,
                        },
                    },
                    {
                        "label": "2 — A little me",
                        "scores": {
                            "Active learner": 2,
                            "Structured learner": 0,
                            "Passive learner": 0,
                            "Buddy/Social learner": 0,
                        },
                    },
                    {
                        "label": "3 — Sometimes me",
                        "scores": {
                            "Active learner": 3,
                            "Structured learner": 0,
                            "Passive learner": 0,
                            "Buddy/Social learner": 0,
                        },
                    },
                    {
                        "label": "4 — Mostly me",
                        "scores": {
                            "Active learner": 4,
                            "Structured learner": 0,
                            "Passive learner": 0,
                            "Buddy/Social learner": 0,
                        },
                    },
                    {
                        "label": "5 — So me!",
                        "scores": {
                            "Active learner": 5,
                            "Structured learner": 0,
                            "Passive learner": 0,
                            "Buddy/Social learner": 0,
                        },
                    },
                ],
            },
            {
                "id": "q2",
                "text": (
                    "A tiny action mission (e.g., 10 ninja steps or desk push-ups) "
                    "helps my brain get ready."
                ),
                "options": [
                    {
                        "label": "1 — Not helpful",
                        "scores": {
                            "Active learner": 1,
                            "Structured learner": 0,
                            "Passive learner": 0,
                            "Buddy/Social learner": 0,
                        },
                    },
                    {
                        "label": "2 — A little helpful",
                        "scores": {
                            "Active learner": 2,
                            "Structured learner": 0,
                            "Passive learner": 0,
                            "Buddy/Social learner": 0,
                        },
                    },
                    {
                        "label": "3 — Not sure",
                        "scores": {
                            "Active learner": 3,
                            "Structured learner": 0,
                            "Passive learner": 0,
                            "Buddy/Social learner": 0,
                        },
                    },
                    {
                        "label": "4 — Mostly helpful",
                        "scores": {
                            "Active learner": 4,
                            "Structured learner": 0,
                            "Passive learner": 0,
                            "Buddy/Social learner": 0,
                        },
                    },
                    {
                        "label": "5 — Super helpful",
                        "scores": {
                            "Active learner": 5,
                            "Structured learner": 0,
                            "Passive learner": 0,
                            "Buddy/Social learner": 0,
                        },
                    },
                ],
            },
            {
                "id": "q3",
                "text": "Maps, recipe cards, or numbered pictures help me know what to do next.",
                "options": [
                    {
                        "label": "1 — Not me",
                        "scores": {
                            "Active learner": 0,
                            "Structured learner": 1,
                            "Passive learner": 0,
                            "Buddy/Social learner": 0,
                        },
                    },
                    {
                        "label": "2 — A little me",
                        "scores": {
                            "Active learner": 0,
                            "Structured learner": 2,
                            "Passive learner": 0,
                            "Buddy/Social learner": 0,
                        },
                    },
                    {
                        "label": "3 — Sometimes me",
                        "scores": {
                            "Active learner": 0,
                            "Structured learner": 3,
                            "Passive learner": 0,
                            "Buddy/Social learner": 0,
                        },
                    },
                    {
                        "label": "4 — Mostly me",
                        "scores": {
                            "Active learner": 0,
                            "Structured learner": 4,
                            "Passive learner": 0,
                            "Buddy/Social learner": 0,
                        },
                    },
                    {
                        "label": "5 — So me!",
                        "scores": {
                            "Active learner": 0,
                            "Structured learner": 5,
                            "Passive learner": 0,
                            "Buddy/Social learner": 0,
                        },
                    },
                ],
            },
            {
                "id": "q4",
                "text": "Putting my ideas into tidy boxes (a plan or checklist) helps me focus.",
                "options": [
                    {
                        "label": "1 — Not me",
                        "scores": {
                            "Active learner": 0,
                            "Structured learner": 1,
                            "Passive learner": 0,
                            "Buddy/Social learner": 0,
                        },
                    },
                    {
                        "label": "2 — A little me",
                        "scores": {
                            "Active learner": 0,
                            "Structured learner": 2,
                            "Passive learner": 0,
                            "Buddy/Social learner": 0,
                        },
                    },
                    {
                        "label": "3 — Sometimes me",
                        "scores": {
                            "Active learner": 0,
                            "Structured learner": 3,
                            "Passive learner": 0,
                            "Buddy/Social learner": 0,
                        },
                    },
                    {
                        "label": "4 — Mostly me",
                        "scores": {
                            "Active learner": 0,
                            "Structured learner": 4,
                            "Passive learner": 0,
                            "Buddy/Social learner": 0,
                        },
                    },
                    {
                        "label": "5 — So me!",
                        "scores": {
                            "Active learner": 0,
                            "Structured learner": 5,
                            "Passive learner": 0,
                            "Buddy/Social learner": 0,
                        },
                    },
                ],
            },
            {
                "id": "q5",
                "text": "My animal-energy meter right now is…",
                "options": [
                    {
                        "label": "1 — Sleepy  panda",
                        "scores": {
                            "Active learner": 0,
                            "Structured learner": 0,
                            "Passive learner": 5,
                            "Buddy/Social learner": 0,
                        },
                    },
                    {
                        "label": "2 — Slow  turtle",
                        "scores": {
                            "Active learner": 0,
                            "Structured learner": 0,
                            "Passive learner": 4,
                            "Buddy/Social learner": 0,
                        },
                    },
                    {
                        "label": "3 — Steady  cat",
                        "scores": {
                            "Active learner": 0,
                            "Structured learner": 0,
                            "Passive learner": 3,
                            "Buddy/Social learner": 0,
                        },
                    },
                    {
                        "label": "4 — Zippy  rabbit",
                        "scores": {
                            "Active learner": 0,
                            "Structured learner": 0,
                            "Passive learner": 2,
                            "Buddy/Social learner": 0,
                        },
                    },
                    {
                        "label": "5 — Rocket  cheetah",
                        "scores": {
                            "Active learner": 0,
                            "Structured learner": 0,
                            "Passive learner": 1,
                            "Buddy/Social learner": 0,
                        },
                    },
                ],
            },
            {
                "id": "q6",
                "text": "My tummy butterflies right now feel like…",
                "options": [
                    {
                        "label": "1 — None  (calm ocean)",
                        "scores": {
                            "Active learner": 0,
                            "Structured learner": 0,
                            "Passive learner": 1,
                            "Buddy/Social learner": 0,
                        },
                    },
                    {
                        "label": "2 — A few ",
                        "scores": {
                            "Active learner": 0,
                            "Structured learner": 0,
                            "Passive learner": 2,
                            "Buddy/Social learner": 0,
                        },
                    },
                    {
                        "label": "3 — Some  buzzing",
                        "scores": {
                            "Active learner": 0,
                            "Structured learner": 0,
                            "Passive learner": 3,
                            "Buddy/Social learner": 0,
                        },
                    },
                    {
                        "label": "4 — Many  fluttering",
                        "scores": {
                            "Active learner": 0,
                            "Structured learner": 0,
                            "Passive learner": 4,
                            "Buddy/Social learner": 0,
                        },
                    },
                    {
                        "label": "5 — A storm  in my belly",
                        "scores": {
                            "Active learner": 0,
                            "Structured learner": 0,
                            "Passive learner": 5,
                            "Buddy/Social learner": 0,
                        },
                    },
                ],
            },
            {
                "id": "q7",
                "text": "Working with a buddy helps me learn.",
                "options": [
                    {
                        "label": "1 — Not at all",
                        "scores": {
                            "Active learner": 0,
                            "Structured learner": 0,
                            "Passive learner": 0,
                            "Buddy/Social learner": 1,
                        },
                    },
                    {
                        "label": "2 — A little",
                        "scores": {
                            "Active learner": 0,
                            "Structured learner": 0,
                            "Passive learner": 0,
                            "Buddy/Social learner": 2,
                        },
                    },
                    {
                        "label": "3 — Not sure",
                        "scores": {
                            "Active learner": 0,
                            "Structured learner": 0,
                            "Passive learner": 0,
                            "Buddy/Social learner": 3,
                        },
                    },
                    {
                        "label": "4 — Mostly",
                        "scores": {
                            "Active learner": 0,
                            "Structured learner": 0,
                            "Passive learner": 0,
                            "Buddy/Social learner": 4,
                        },
                    },
                    {
                        "label": "5 — Yes, a lot",
                        "scores": {
                            "Active learner": 0,
                            "Structured learner": 0,
                            "Passive learner": 0,
                            "Buddy/Social learner": 5,
                        },
                    },
                ],
            },
            {
                "id": "q8",
                "text": "I feel braver when I can share ideas with a partner.",
                "options": [
                    {
                        "label": "1 — Not at all",
                        "scores": {
                            "Active learner": 0,
                            "Structured learner": 0,
                            "Passive learner": 0,
                            "Buddy/Social learner": 1,
                        },
                    },
                    {
                        "label": "2 — A little",
                        "scores": {
                            "Active learner": 0,
                            "Structured learner": 0,
                            "Passive learner": 0,
                            "Buddy/Social learner": 2,
                        },
                    },
                    {
                        "label": "3 — Not sure",
                        "scores": {
                            "Active learner": 0,
                            "Structured learner": 0,
                            "Passive learner": 0,
                            "Buddy/Social learner": 3,
                        },
                    },
                    {
                        "label": "4 — Mostly",
                        "scores": {
                            "Active learner": 0,
                            "Structured learner": 0,
                            "Passive learner": 0,
                            "Buddy/Social learner": 4,
                        },
                    },
                    {
                        "label": "5 — Yes, a lot",
                        "scores": {
                            "Active learner": 0,
                            "Structured learner": 0,
                            "Passive learner": 0,
                            "Buddy/Social learner": 5,
                        },
                    },
                ],
            },
            {
                "id": "q9",
                "text": "Choose your starter power-up for today:",
                "options": [
                    {
                        "label": "A — Kangaroo hops  (10 gentle jumps by your desk)",
                        "scores": {
                            "Active learner": 5,
                            "Structured learner": 0,
                            "Passive learner": 0,
                            "Buddy/Social learner": 0,
                        },
                    },
                    {
                        "label": "B — Wise owl  plan card (goal + 3 steps)",
                        "scores": {
                            "Active learner": 0,
                            "Structured learner": 5,
                            "Passive learner": 0,
                            "Buddy/Social learner": 0,
                        },
                    },
                    {
                        "label": "C — Cozy sloth  calm minute (slow breath + mini video)",
                        "scores": {
                            "Active learner": 0,
                            "Structured learner": 0,
                            "Passive learner": 5,
                            "Buddy/Social learner": 0,
                        },
                    },
                    {
                        "label": "D — Penguin pals  pair-chat (share ideas for 1 minute)",
                        "scores": {
                            "Active learner": 0,
                            "Structured learner": 0,
                            "Passive learner": 0,
                            "Buddy/Social learner": 5,
                        },
                    },
                ],
            },
            {
                "id": "q10",
                "text": "When a puzzle gets tricky, I grab this helper:",
                "options": [
                    {
                        "label": "A — Builder gloves  (act it out with hands/body)",
                        "scores": {
                            "Active learner": 5,
                            "Structured learner": 0,
                            "Passive learner": 0,
                            "Buddy/Social learner": 0,
                        },
                    },
                    {
                        "label": "B — Step ladder  (numbered example or checklist)",
                        "scores": {
                            "Active learner": 0,
                            "Structured learner": 5,
                            "Passive learner": 0,
                            "Buddy/Social learner": 0,
                        },
                    },
                    {
                        "label": "C — Cloud pillow  (quiet pause to reset)",
                        "scores": {
                            "Active learner": 0,
                            "Structured learner": 0,
                            "Passive learner": 5,
                            "Buddy/Social learner": 0,
                        },
                    },
                    {
                        "label": "D — Walkie-talkie  (ask a buddy to think with me)",
                        "scores": {
                            "Active learner": 0,
                            "Structured learner": 0,
                            "Passive learner": 0,
                            "Buddy/Social learner": 5,
                        },
                    },
                ],
            },
        ]

        db.execute(
            text(
                """
                INSERT INTO surveys (id, title, questions_json, creator_name, created_at)
                VALUES (:id, :title, :questions_json, :creator_name, now())
                """
            ),
            {
                "id": survey_2_id,
                "title": survey_2_title,
                "questions_json": json.dumps(survey_2_questions),
                "creator_name": "system",
            },
        )
        print(f"✅ Created survey: {survey_2_title}")

        # -----------------------------
        # 6) Create sessions  (sessions: id, course_id, survey_template_id, join_token, started_at)
        # -----------------------------
        print("🗓️ Creating sample sessions...")

        session_1_id = str(uuid.uuid4())
        join_token_1 = "LEARN123"  # unique
        db.execute(
            text(
                """
                INSERT INTO sessions (id, course_id, survey_template_id, join_token, started_at)
                VALUES (:id, :course_id, :survey_template_id, :join_token, now())
                """
            ),
            {
                "id": session_1_id,
                "course_id": course_id,
                "survey_template_id": survey_1_id,
                "join_token": join_token_1,
            },
        )
        print(f"✅ Created session for '{course_title}' with join token '{join_token_1}'")

        session_2_id = str(uuid.uuid4())
        join_token_2 = "QUEST456"
        db.execute(
            text(
                """
                INSERT INTO sessions (id, course_id, survey_template_id, join_token, started_at)
                VALUES (:id, :course_id, :survey_template_id, :join_token, now())
                """
            ),
            {
                "id": session_2_id,
                "course_id": course_id,
                "survey_template_id": survey_2_id,
                "join_token": join_token_2,
            },
        )
        print(f"✅ Created session for '{course_title}' with join token '{join_token_2}'")

        # -----------------------------
        # 7) Create submissions (respect check/unique constraints)
        # -----------------------------
        print("📥 Creating sample submissions...")

        # Submission 1: Authenticated student (guest_* must be NULL)
        answers_1 = {
            "q1": "4 — Mostly",
            "q2": "5 — Yes, a lot",
            "q3": "3 — Not sure",
            "q4": "4 — Mostly",
            "q5": "3 — Okay",
            "q6": "2 — A little worried",
            "q7": "A —  Move break",
            "q8": "A — Try it with hands/body",
            "q9": "A — Quick game / movement challenge",
        }
        total_scores_1 = calculate_sample_scores(answers_1, survey_1_questions)
        db.execute(
            text(
                """
                INSERT INTO submissions
                (id, session_id, student_id, guest_name, guest_id, 
                 answers_json, total_scores, status, created_at)
                VALUES
                (:id, :session_id, :student_id, NULL, NULL, 
                 :answers_json, :total_scores, :status, now())
                """
            ),
            {
                "id": str(uuid.uuid4()),
                "session_id": session_1_id,
                "student_id": student_1_id,  # 学生提交：guest_* 必须为 NULL
                "answers_json": json.dumps(answers_1),
                "total_scores": json.dumps(total_scores_1),
                "status": "completed",
            },
        )
        print(f"✅ Created authenticated submission for {student_1_email}")

        # Submission 2: Guest submission (student_id NULL, guest_* non-null)
        guest_name = "Guest Student"
        guest_uuid = str(uuid.uuid4())
        answers_2 = {
            "q1": "4 — Mostly me",
            "q2": "4 — Mostly helpful",
            "q3": "5 — So me!",
            "q4": "3 — Sometimes me",
            "q5": "2 — Slow  turtle",
            "q6": "3 — Some  buzzing",
            "q7": "4 — Mostly",
            "q8": "4 — Mostly",
            "q9": "D — Penguin pals  pair-chat (share ideas for 1 minute)",
            "q10": "D — Walkie-talkie  (ask a buddy to think with me)",
        }
        total_scores_2 = calculate_sample_scores(answers_2, survey_2_questions)
        db.execute(
            text(
                """
                INSERT INTO submissions
                (id, session_id, student_id, guest_name, guest_id, 
                 answers_json, total_scores, status, created_at)
                VALUES
                (:id, :session_id, NULL, :guest_name, :guest_id, 
                 :answers_json, :total_scores, :status, now())
                """
            ),
            {
                "id": str(uuid.uuid4()),
                "session_id": session_2_id,
                "guest_name": guest_name,
                "guest_id": guest_uuid,  # 游客必须提供 guest_id
                "answers_json": json.dumps(answers_2),
                "total_scores": json.dumps(total_scores_2),
                "status": "completed",
            },
        )
        print(f"✅ Created guest submission for '{guest_name}'")

        # Submission 3: Another authenticated student
        answers_3 = {
            "q1": "2 — A little",
            "q2": "3 — Not sure",
            "q3": "5 — Yes, a lot",
            "q4": "4 — Mostly",
            "q5": "4 — High",
            "q6": "1 — Not worried",
            "q7": "C — Lesson preview",
            "q8": "B — Look at an example or steps",
            "q9": "B — Picture card of today's steps",
        }
        total_scores_3 = calculate_sample_scores(answers_3, survey_1_questions)
        db.execute(
            text(
                """
                INSERT INTO submissions
                (id, session_id, student_id, guest_name, guest_id, 
                 answers_json, total_scores, status, created_at)
                VALUES
                (:id, :session_id, :student_id, NULL, NULL, 
                 :answers_json, :total_scores, :status, now())
                """
            ),
            {
                "id": str(uuid.uuid4()),
                "session_id": session_1_id,
                "student_id": student_2_id,
                "answers_json": json.dumps(answers_3),
                "total_scores": json.dumps(total_scores_3),
                "status": "completed",
            },
        )
        print(f"✅ Created authenticated submission for {student_2_email}")

        # -----------------------------
        # 8) Commit & summary
        # -----------------------------
        db.commit()
        print("\n🎉 Seeding complete!")
        print("\n📊 Summary:")
        print(f"  - Teacher: {teacher_email} ({teacher_full_name})")
        print(
            f"  - Students: {student_1_email} ({student_1_full_name}), "
            f"{student_2_email} ({student_2_full_name})"
        )
        print(f"  - Course: {course_title}")
        print("  - Surveys: 2 new surveys created")
        print("  - Sessions: 2 sessions with join tokens")
        print("  - Submissions: 3 (2 authenticated + 1 guest)")
        print("\n🔑 Test Credentials:")
        print(f"  - Teacher Login: {teacher_email} / Passw0rd!")
        print(f"  - Student 1 Login: {student_1_email} / Passw0rd!")
        print(f"  - Student 2 Login: {student_2_email} / Passw0rd!")
        print(f"  - Join Tokens: {join_token_1}, {join_token_2}")

    except Exception as e:
        db.rollback()
        print(f"❌ Error seeding data: {e}")
        raise
    finally:
        db.close()


if __name__ == "__main__":
    seed_data()
