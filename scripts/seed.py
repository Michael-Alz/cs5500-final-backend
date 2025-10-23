#!/usr/bin/env python3
"""
New Seed Script with Updated Surveys

This script seeds the database with the new survey templates:
- Learning Buddy: Style Check
- Critter Quest: Learning Adventure
"""

import json
import sys
import uuid
from pathlib import Path

from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker

# Adjust path to import app modules
project_root = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(project_root))

from app.core.config import settings  # noqa: E402
from app.core.security import hash_password  # noqa: E402

# Database setup
SQLALCHEMY_DATABASE_URL = settings.database_url
engine = create_engine(SQLALCHEMY_DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def calculate_sample_scores(answers: dict, survey_template_questions: list) -> dict:
    """Calculate total scores for each category based on sample student answers."""
    all_categories = set()
    for question in survey_template_questions:
        for option in question.get("options", []):
            scores = option.get("scores", {})
            all_categories.update(scores.keys())

    total_scores = {category: 0 for category in all_categories}

    for question in survey_template_questions:
        question_id = question.get("id")
        if question_id not in answers:
            continue

        selected_answer = answers[question_id]

        for option in question.get("options", []):
            if option.get("label") == selected_answer:
                scores = option.get("scores", {})
                for category, score in scores.items():
                    if category in total_scores:
                        total_scores[category] += score
                break
    return total_scores


def seed_data() -> None:
    """Seed the database with essential data."""
    db = SessionLocal()
    try:
        print("🌱 Starting database seeding...")

        # Clear existing data in correct order (respecting foreign keys)
        print("🗑️  Clearing existing data...")
        try:
            db.execute(text("DELETE FROM submissions"))
        except Exception:
            pass  # Table might not exist
        try:
            db.execute(text("DELETE FROM sessions"))
        except Exception:
            pass  # Table might not exist
        try:
            db.execute(text("DELETE FROM courses"))
        except Exception:
            pass  # Table might not exist
        try:
            db.execute(text("DELETE FROM surveys"))
        except Exception:
            pass  # Table might not exist
        try:
            db.execute(text("DELETE FROM teachers"))
        except Exception:
            pass  # Table might not exist
        db.commit()
        print("✅ Cleared existing data")

        # Create teacher
        teacher_id = str(uuid.uuid4())
        teacher_email = "teacher1@example.com"
        hashed_password = hash_password("Passw0rd!")

        db.execute(
            text(
                "INSERT INTO teachers (id, email, password_hash, created_at) VALUES "
                "(:id, :email, :password_hash, now())"
            ),
            {"id": teacher_id, "email": teacher_email, "password_hash": hashed_password},
        )
        print(f"✅ Created teacher: {teacher_email}")

        # Create course
        course_id = str(uuid.uuid4())
        course_title = "CS101 — Intro Class"

        db.execute(
            text(
                "INSERT INTO courses (id, title, teacher_id, created_at) VALUES "
                "(:id, :title, :teacher_id, now())"
            ),
            {"id": course_id, "title": course_title, "teacher_id": teacher_id},
        )
        print(f"✅ Created course: {course_title}")

        # Create surveys
        print("📝 Creating new surveys...")

        # Survey 1: Learning Buddy: Style Check
        survey_1_id = str(uuid.uuid4())
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
                "INSERT INTO surveys (id, title, questions_json, creator_name, created_at) VALUES "
                "(:id, :title, :questions_json, :creator_name, now())"
            ),
            {
                "id": survey_1_id,
                "title": "Learning Buddy: Style Check",
                "questions_json": json.dumps(survey_1_questions),
                "creator_name": "system",
            },
        )
        print("✅ Created survey: Learning Buddy: Style Check")

        # Survey 2: Critter Quest: Learning Adventure
        survey_2_id = str(uuid.uuid4())
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
                "INSERT INTO surveys (id, title, questions_json, creator_name, created_at) VALUES "
                "(:id, :title, :questions_json, :creator_name, now())"
            ),
            {
                "id": survey_2_id,
                "title": "Critter Quest: Learning Adventure",
                "questions_json": json.dumps(survey_2_questions),
                "creator_name": "system",
            },
        )
        print("✅ Created survey: Critter Quest: Learning Adventure")

        # Create sessions
        print("🗓️ Creating sample sessions...")
        session_1_id = str(uuid.uuid4())
        join_token_1 = "LEARN123"
        db.execute(
            text(
                "INSERT INTO sessions (id, course_id, survey_template_id, join_token, started_at) "
                "VALUES "
                "(:id, :course_id, :survey_template_id, :join_token, now())"
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
                "INSERT INTO sessions (id, course_id, survey_template_id, join_token, started_at) "
                "VALUES "
                "(:id, :course_id, :survey_template_id, :join_token, now())"
            ),
            {
                "id": session_2_id,
                "course_id": course_id,
                "survey_template_id": survey_2_id,
                "join_token": join_token_2,
            },
        )
        print(f"✅ Created session for '{course_title}' with join token '{join_token_2}'")

        # Create sample submissions
        print("📥 Creating sample submissions...")

        # Sample submission for Learning Buddy survey
        student_name_1 = "Alex Johnson"
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
                "INSERT INTO submissions (id, session_id, student_name, answers_json, "
                "total_scores, created_at) "
                "VALUES "
                "(:id, :session_id, :student_name, :answers_json, :total_scores, now())"
            ),
            {
                "id": str(uuid.uuid4()),
                "session_id": session_1_id,
                "student_name": student_name_1,
                "answers_json": json.dumps(answers_1),
                "total_scores": json.dumps(total_scores_1),
            },
        )
        print(f"✅ Created submission for '{student_name_1}' in session '{join_token_1}'")

        # Sample submission for Critter Quest survey
        student_name_2 = "Maya Chen"
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
                "INSERT INTO submissions (id, session_id, student_name, answers_json, "
                "total_scores, created_at) "
                "VALUES "
                "(:id, :session_id, :student_name, :answers_json, :total_scores, now())"
            ),
            {
                "id": str(uuid.uuid4()),
                "session_id": session_2_id,
                "student_name": student_name_2,
                "answers_json": json.dumps(answers_2),
                "total_scores": json.dumps(total_scores_2),
            },
        )
        print(f"✅ Created submission for '{student_name_2}' in session '{join_token_2}'")

        db.commit()
        print("\n🎉 Seeding complete!")
        print("\n📊 Summary:")
        print(f"  - Teacher: {teacher_email}")
        print(f"  - Course: {course_title}")
        print("  - Surveys: 2 new surveys created")
        print("  - Sessions: 2 sessions with join tokens")
        print("  - Submissions: 2 sample submissions with calculated scores")

    except Exception as e:
        print(f"❌ Error seeding data: {e}")
        db.rollback()
        raise
    finally:
        db.close()


if __name__ == "__main__":
    seed_data()
