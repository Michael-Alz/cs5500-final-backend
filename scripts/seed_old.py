#!/usr/bin/env python3
"""
Simple database seeding script for 5500 Backend.
This script populates the database with essential data for development.
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
        survey_a_id = str(uuid.uuid4())
        survey_b_id = str(uuid.uuid4())

        # Survey A questions
        survey_a_questions = [
            {
                "id": "q1",
                "text": "I prefer to learn by doing hands-on activities.",
                "options": [
                    {
                        "label": "Strongly agree",
                        "scores": {
                            "Active learner": 5,
                            "Structured learner": 0,
                            "Balanced learner": 0,
                        },
                    },
                    {
                        "label": "Prefer structured guidance",
                        "scores": {
                            "Active learner": 0,
                            "Structured learner": 5,
                            "Balanced learner": 0,
                        },
                    },
                    {
                        "label": "A bit of both",
                        "scores": {
                            "Active learner": 0,
                            "Structured learner": 0,
                            "Balanced learner": 5,
                        },
                    },
                ],
            },
            {
                "id": "q2",
                "text": "I learn best when I can see the big picture first.",
                "options": [
                    {
                        "label": "Strongly agree",
                        "scores": {
                            "Active learner": 5,
                            "Structured learner": 0,
                            "Balanced learner": 0,
                        },
                    },
                    {
                        "label": "Prefer step-by-step",
                        "scores": {
                            "Active learner": 0,
                            "Structured learner": 5,
                            "Balanced learner": 0,
                        },
                    },
                    {
                        "label": "A bit of both",
                        "scores": {
                            "Active learner": 0,
                            "Structured learner": 0,
                            "Balanced learner": 5,
                        },
                    },
                ],
            },
            {
                "id": "q3",
                "text": "I enjoy working in groups and discussing ideas.",
                "options": [
                    {
                        "label": "Strongly agree",
                        "scores": {
                            "Active learner": 5,
                            "Structured learner": 0,
                            "Balanced learner": 0,
                        },
                    },
                    {
                        "label": "Prefer individual work",
                        "scores": {
                            "Active learner": 0,
                            "Structured learner": 5,
                            "Balanced learner": 0,
                        },
                    },
                    {
                        "label": "A bit of both",
                        "scores": {
                            "Active learner": 0,
                            "Structured learner": 0,
                            "Balanced learner": 5,
                        },
                    },
                ],
            },
            {
                "id": "q4",
                "text": "I need clear instructions and examples to understand new concepts.",
                "options": [
                    {
                        "label": "Strongly agree",
                        "scores": {
                            "Active learner": 0,
                            "Structured learner": 5,
                            "Balanced learner": 0,
                        },
                    },
                    {
                        "label": "Prefer to figure it out myself",
                        "scores": {
                            "Active learner": 5,
                            "Structured learner": 0,
                            "Balanced learner": 0,
                        },
                    },
                    {
                        "label": "A bit of both",
                        "scores": {
                            "Active learner": 0,
                            "Structured learner": 0,
                            "Balanced learner": 5,
                        },
                    },
                ],
            },
            {
                "id": "q5",
                "text": "I like to experiment and try different approaches.",
                "options": [
                    {
                        "label": "Strongly agree",
                        "scores": {
                            "Active learner": 5,
                            "Structured learner": 0,
                            "Balanced learner": 0,
                        },
                    },
                    {
                        "label": "Prefer proven methods",
                        "scores": {
                            "Active learner": 0,
                            "Structured learner": 5,
                            "Balanced learner": 0,
                        },
                    },
                    {
                        "label": "A bit of both",
                        "scores": {
                            "Active learner": 0,
                            "Structured learner": 0,
                            "Balanced learner": 5,
                        },
                    },
                ],
            },
            {
                "id": "q6",
                "text": "I work best with deadlines and clear schedules.",
                "options": [
                    {
                        "label": "Strongly agree",
                        "scores": {
                            "Active learner": 0,
                            "Structured learner": 5,
                            "Balanced learner": 0,
                        },
                    },
                    {
                        "label": "Prefer flexible timing",
                        "scores": {
                            "Active learner": 5,
                            "Structured learner": 0,
                            "Balanced learner": 0,
                        },
                    },
                    {
                        "label": "A bit of both",
                        "scores": {
                            "Active learner": 0,
                            "Structured learner": 0,
                            "Balanced learner": 5,
                        },
                    },
                ],
            },
            {
                "id": "q7",
                "text": "I learn best by reading and taking notes.",
                "options": [
                    {
                        "label": "Strongly agree",
                        "scores": {
                            "Active learner": 0,
                            "Structured learner": 5,
                            "Balanced learner": 0,
                        },
                    },
                    {
                        "label": "Prefer visual/audio learning",
                        "scores": {
                            "Active learner": 5,
                            "Structured learner": 0,
                            "Balanced learner": 0,
                        },
                    },
                    {
                        "label": "A bit of both",
                        "scores": {
                            "Active learner": 0,
                            "Structured learner": 0,
                            "Balanced learner": 5,
                        },
                    },
                ],
            },
            {
                "id": "q8",
                "text": "I like to ask questions and challenge ideas.",
                "options": [
                    {
                        "label": "Strongly agree",
                        "scores": {
                            "Active learner": 5,
                            "Structured learner": 0,
                            "Balanced learner": 0,
                        },
                    },
                    {
                        "label": "Prefer to follow established rules",
                        "scores": {
                            "Active learner": 0,
                            "Structured learner": 5,
                            "Balanced learner": 0,
                        },
                    },
                    {
                        "label": "A bit of both",
                        "scores": {
                            "Active learner": 0,
                            "Structured learner": 0,
                            "Balanced learner": 5,
                        },
                    },
                ],
            },
        ]

        # Survey B questions (different set)
        survey_b_questions = [
            {
                "id": "q1",
                "text": "I prefer to work at my own pace without pressure.",
                "options": [
                    {
                        "label": "Strongly agree",
                        "scores": {
                            "Active learner": 5,
                            "Structured learner": 0,
                            "Balanced learner": 0,
                        },
                    },
                    {
                        "label": "Prefer structured deadlines",
                        "scores": {
                            "Active learner": 0,
                            "Structured learner": 5,
                            "Balanced learner": 0,
                        },
                    },
                    {
                        "label": "A bit of both",
                        "scores": {
                            "Active learner": 0,
                            "Structured learner": 0,
                            "Balanced learner": 5,
                        },
                    },
                ],
            },
            {
                "id": "q2",
                "text": "I like to understand the theory before applying it.",
                "options": [
                    {
                        "label": "Strongly agree",
                        "scores": {
                            "Active learner": 0,
                            "Structured learner": 5,
                            "Balanced learner": 0,
                        },
                    },
                    {
                        "label": "Prefer learning by doing",
                        "scores": {
                            "Active learner": 5,
                            "Structured learner": 0,
                            "Balanced learner": 0,
                        },
                    },
                    {
                        "label": "A bit of both",
                        "scores": {
                            "Active learner": 0,
                            "Structured learner": 0,
                            "Balanced learner": 5,
                        },
                    },
                ],
            },
            {
                "id": "q3",
                "text": "I enjoy brainstorming and creative problem-solving.",
                "options": [
                    {
                        "label": "Strongly agree",
                        "scores": {
                            "Active learner": 5,
                            "Structured learner": 0,
                            "Balanced learner": 0,
                        },
                    },
                    {
                        "label": "Prefer systematic approaches",
                        "scores": {
                            "Active learner": 0,
                            "Structured learner": 5,
                            "Balanced learner": 0,
                        },
                    },
                    {
                        "label": "A bit of both",
                        "scores": {
                            "Active learner": 0,
                            "Structured learner": 0,
                            "Balanced learner": 5,
                        },
                    },
                ],
            },
            {
                "id": "q4",
                "text": "I need detailed feedback to improve my work.",
                "options": [
                    {
                        "label": "Strongly agree",
                        "scores": {
                            "Active learner": 0,
                            "Structured learner": 5,
                            "Balanced learner": 0,
                        },
                    },
                    {
                        "label": "Prefer general guidance",
                        "scores": {
                            "Active learner": 5,
                            "Structured learner": 0,
                            "Balanced learner": 0,
                        },
                    },
                    {
                        "label": "A bit of both",
                        "scores": {
                            "Active learner": 0,
                            "Structured learner": 0,
                            "Balanced learner": 5,
                        },
                    },
                ],
            },
            {
                "id": "q5",
                "text": "I like to explore multiple solutions to problems.",
                "options": [
                    {
                        "label": "Strongly agree",
                        "scores": {
                            "Active learner": 5,
                            "Structured learner": 0,
                            "Balanced learner": 0,
                        },
                    },
                    {
                        "label": "Prefer the best single solution",
                        "scores": {
                            "Active learner": 0,
                            "Structured learner": 5,
                            "Balanced learner": 0,
                        },
                    },
                    {
                        "label": "A bit of both",
                        "scores": {
                            "Active learner": 0,
                            "Structured learner": 0,
                            "Balanced learner": 5,
                        },
                    },
                ],
            },
            {
                "id": "q6",
                "text": "I work best with clear objectives and milestones.",
                "options": [
                    {
                        "label": "Strongly agree",
                        "scores": {
                            "Active learner": 0,
                            "Structured learner": 5,
                            "Balanced learner": 0,
                        },
                    },
                    {
                        "label": "Prefer open-ended exploration",
                        "scores": {
                            "Active learner": 5,
                            "Structured learner": 0,
                            "Balanced learner": 0,
                        },
                    },
                    {
                        "label": "A bit of both",
                        "scores": {
                            "Active learner": 0,
                            "Structured learner": 0,
                            "Balanced learner": 5,
                        },
                    },
                ],
            },
            {
                "id": "q7",
                "text": "I learn best through interactive activities and discussions.",
                "options": [
                    {
                        "label": "Strongly agree",
                        "scores": {
                            "Active learner": 5,
                            "Structured learner": 0,
                            "Balanced learner": 0,
                        },
                    },
                    {
                        "label": "Prefer lectures and presentations",
                        "scores": {
                            "Active learner": 0,
                            "Structured learner": 5,
                            "Balanced learner": 0,
                        },
                    },
                    {
                        "label": "A bit of both",
                        "scores": {
                            "Active learner": 0,
                            "Structured learner": 0,
                            "Balanced learner": 5,
                        },
                    },
                ],
            },
            {
                "id": "q8",
                "text": "I like to follow established procedures and protocols.",
                "options": [
                    {
                        "label": "Strongly agree",
                        "scores": {
                            "Active learner": 0,
                            "Structured learner": 5,
                            "Balanced learner": 0,
                        },
                    },
                    {
                        "label": "Prefer to create my own methods",
                        "scores": {
                            "Active learner": 5,
                            "Structured learner": 0,
                            "Balanced learner": 0,
                        },
                    },
                    {
                        "label": "A bit of both",
                        "scores": {
                            "Active learner": 0,
                            "Structured learner": 0,
                            "Balanced learner": 5,
                        },
                    },
                ],
            },
        ]

        # Insert Survey A
        db.execute(
            text(
                "INSERT INTO surveys (id, title, questions_json, creator_name, created_at) VALUES "
                "(:id, :title, :questions_json, :creator_name, now())"
            ),
            {
                "id": survey_a_id,
                "title": "Learning Style Survey A",
                "questions_json": json.dumps(survey_a_questions),
                "creator_name": "system",
            },
        )
        print("✅ Created survey: Learning Style Survey A")

        # Insert Survey B
        db.execute(
            text(
                "INSERT INTO surveys (id, title, questions_json, creator_name, created_at) VALUES "
                "(:id, :title, :questions_json, :creator_name, now())"
            ),
            {
                "id": survey_b_id,
                "title": "Learning Style Survey B",
                "questions_json": json.dumps(survey_b_questions),
                "creator_name": "system",
            },
        )
        print("✅ Created survey: Learning Style Survey B")

        db.commit()
        print("\n🎉 Seeding complete!")

    except Exception as e:
        print(f"❌ Error seeding data: {e}")
        db.rollback()
        raise
    finally:
        db.close()


if __name__ == "__main__":
    seed_data()
