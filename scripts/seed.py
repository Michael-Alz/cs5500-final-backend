#!/usr/bin/env python3
"""
Seed the database with sample data that matches the latest product spec.

This script will:
1. Wipe existing demo data (teachers, students, surveys, courses, sessions, etc.).
2. Insert one teacher and two students.
3. Create a baseline learning-style survey.
4. Create one course linked to the survey (with mood labels + learning style categories).
5. Add activity types, activities, and course recommendations.
6. Spin up two sessions (one requires the survey, one mood-only).
7. Insert submissions (student + guest) and maintain course_student_profiles.

Run with: ``uv run python scripts/seed.py`` (after applying migrations).
"""

import sys
import uuid
from pathlib import Path
from typing import Dict, List, Tuple

from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker

# Allow importing the app package when running as a script.
project_root = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(project_root))

from app.core.config import settings  # noqa: E402
from app.core.security import hash_password  # noqa: E402
from app.models import (  # noqa: E402
    Activity,
    ActivityType,
    ClassSession,
    Course,
    CourseRecommendation,
    CourseStudentProfile,
    Student,
    Submission,
    SurveyTemplate,
    Teacher,
)
from app.services.surveys import (  # noqa: E402
    build_survey_snapshot,
    compute_total_scores,
    determine_learning_style,
    extract_learning_style_categories,
)

SQLALCHEMY_DATABASE_URL = settings.database_url
engine = create_engine(SQLALCHEMY_DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def reset_database(db: Session) -> None:
    """Remove existing demo data in a FK-safe order."""
    print("🧽 Clearing existing seed data…")
    for model in (
        CourseStudentProfile,
        CourseRecommendation,
        Submission,
        ClassSession,
        Activity,
        ActivityType,
        Course,
        SurveyTemplate,
        Student,
        Teacher,
    ):
        db.query(model).delete()
    db.commit()
    print("✅ Existing data cleared.")


def create_teacher(db: Session) -> Teacher:
    teacher = Teacher(
        id=str(uuid.uuid4()),
        email="teacher1@example.com",
        password_hash=hash_password("Passw0rd!"),
        full_name="Dr. Riley Smith",
    )
    db.add(teacher)
    db.flush()
    print(f"👩‍🏫 Teacher created: {teacher.email}")
    return teacher


def create_students(db: Session) -> List[Student]:
    students: List[Student] = []
    sample_students = [
        ("student1@example.com", "Alex Johnson"),
        ("student2@example.com", "Maya Chen"),
    ]
    for email, name in sample_students:
        student = Student(
            id=str(uuid.uuid4()),
            email=email,
            password_hash=hash_password("Passw0rd!"),
            full_name=name,
        )
        db.add(student)
        db.flush()
        students.append(student)
        print(f"👨‍🎓 Student created: {email}")
    return students


def create_surveys(db: Session, teacher: Teacher) -> Tuple[SurveyTemplate, List[SurveyTemplate]]:
    """Create the original two surveys from the legacy seed plus return the baseline."""
    survey_1_questions: List[dict] = [
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

    survey_2_questions: List[dict] = [
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
                "A tiny action mission (e.g., 10 ninja steps or desk push-ups) helps my brain get "
                "ready."
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
            "text": "Meeting in a small crew (1-2 people) helps me feel calm and ready.",
            "options": [
                {
                    "label": "1 — Not really",
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
                    "label": "4 — Yes",
                    "scores": {
                        "Active learner": 0,
                        "Structured learner": 0,
                        "Passive learner": 0,
                        "Buddy/Social learner": 4,
                    },
                },
                {
                    "label": "5 — Definitely",
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
            "id": "q5",
            "text": "If my energy feels wobbly, I like to…",
            "options": [
                {
                    "label": "1 — Take a quiet break first",
                    "scores": {
                        "Active learner": 0,
                        "Structured learner": 0,
                        "Passive learner": 5,
                        "Buddy/Social learner": 0,
                    },
                },
                {
                    "label": "2 — Talk to someone about it",
                    "scores": {
                        "Active learner": 0,
                        "Structured learner": 0,
                        "Passive learner": 0,
                        "Buddy/Social learner": 5,
                    },
                },
                {
                    "label": "3 — Do a movement challenge",
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
            "id": "q6",
            "text": "When I get stuck, I like to…",
            "options": [
                {
                    "label": "1 — Try it with hands/body",
                    "scores": {
                        "Active learner": 5,
                        "Structured learner": 0,
                        "Passive learner": 0,
                        "Buddy/Social learner": 0,
                    },
                },
                {
                    "label": "2 — Look at example cards or a video",
                    "scores": {
                        "Active learner": 0,
                        "Structured learner": 5,
                        "Passive learner": 0,
                        "Buddy/Social learner": 0,
                    },
                },
                {
                    "label": "3 — Ask a buddy to explain it with me",
                    "scores": {
                        "Active learner": 0,
                        "Structured learner": 0,
                        "Passive learner": 0,
                        "Buddy/Social learner": 5,
                    },
                },
                {
                    "label": "4 — Take a quiet minute first",
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
            "text": "Which starter helps you most today?",
            "options": [
                {
                    "label": "1 — Quick game / movement challenge",
                    "scores": {
                        "Active learner": 5,
                        "Structured learner": 0,
                        "Passive learner": 0,
                        "Buddy/Social learner": 0,
                    },
                },
                {
                    "label": "2 — Picture card of today's steps",
                    "scores": {
                        "Active learner": 0,
                        "Structured learner": 5,
                        "Passive learner": 0,
                        "Buddy/Social learner": 0,
                    },
                },
                {
                    "label": "3 — Quiet breath + 30-sec video",
                    "scores": {
                        "Active learner": 0,
                        "Structured learner": 0,
                        "Passive learner": 5,
                        "Buddy/Social learner": 0,
                    },
                },
                {
                    "label": "4 — Buddy brainstorm",
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
            "text": "If feedback is confusing, I like to…",
            "options": [
                {
                    "label": "1 — Watch someone demo it again",
                    "scores": {
                        "Active learner": 0,
                        "Structured learner": 5,
                        "Passive learner": 0,
                        "Buddy/Social learner": 0,
                    },
                },
                {
                    "label": "2 — Talk through it with a buddy",
                    "scores": {
                        "Active learner": 0,
                        "Structured learner": 0,
                        "Passive learner": 0,
                        "Buddy/Social learner": 5,
                    },
                },
                {
                    "label": "3 — Try again with movement",
                    "scores": {
                        "Active learner": 5,
                        "Structured learner": 0,
                        "Passive learner": 0,
                        "Buddy/Social learner": 0,
                    },
                },
                {
                    "label": "4 — Take a calm minute first",
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
            "id": "q9",
            "text": "Celebrating a win feels best when…",
            "options": [
                {
                    "label": "1 — I can show or move the new skill",
                    "scores": {
                        "Active learner": 5,
                        "Structured learner": 0,
                        "Passive learner": 0,
                        "Buddy/Social learner": 0,
                    },
                },
                {
                    "label": "2 — I tell someone about it",
                    "scores": {
                        "Active learner": 0,
                        "Structured learner": 0,
                        "Passive learner": 0,
                        "Buddy/Social learner": 5,
                    },
                },
                {
                    "label": "3 — I keep a calm moment for myself",
                    "scores": {
                        "Active learner": 0,
                        "Structured learner": 0,
                        "Passive learner": 5,
                        "Buddy/Social learner": 0,
                    },
                },
            ],
        },
    ]

    survey_1 = SurveyTemplate(
        id=str(uuid.uuid4()),
        title="Learning Buddy: Style Check",
        questions_json=survey_1_questions,
        creator_name=teacher.full_name or "Unknown Teacher",
        creator_id=teacher.id,
        creator_email=teacher.email,
    )
    db.add(survey_1)

    survey_2 = SurveyTemplate(
        id=str(uuid.uuid4()),
        title="Critter Quest: Learning Adventure",
        questions_json=survey_2_questions,
        creator_name=teacher.full_name or "Unknown Teacher",
        creator_id=teacher.id,
        creator_email=teacher.email,
    )
    db.add(survey_2)
    db.flush()

    print("📝 Legacy surveys created (Learning Buddy + Critter Quest).")
    return survey_1, [survey_2]


def create_course(db: Session, teacher: Teacher, baseline: SurveyTemplate) -> Course:
    categories = extract_learning_style_categories(baseline.questions_json or [])
    mood_labels = ["energized", "steady", "worried"]
    course = Course(
        id=str(uuid.uuid4()),
        title="CS101 – Intro Class",
        teacher_id=teacher.id,
        baseline_survey_id=baseline.id,
        learning_style_categories=categories,
        mood_labels=mood_labels,
        requires_rebaseline=True,
    )
    db.add(course)
    db.flush()
    print(f"📘 Course created: {course.title}")
    return course


def seed_default_activity_types_and_activities(
    db: Session, teacher: Teacher | None = None
) -> Dict[str, Activity]:
    """Ensure default activity types and sample activities exist."""

    activity_type_seed_data = [
        {
            "type_name": "in-class-task",
            "description": (
                "Live classroom activity students do immediately (pair work, role-play, hands-on "
                "practice)."
            ),
            "required_fields": ["steps"],
            "optional_fields": [
                "materials_needed",
                "group_size",
                "timing_hint",
                "notes_for_teacher",
            ],
            "example_content_json": {
                "steps": [
                    "Pair up with the person next to you.",
                    "Explain today's topic in your own words for 2 minutes.",
                    "Switch roles and repeat.",
                    "Each person writes one thing they still don't understand.",
                ],
                "materials_needed": ["timer", "paper", "pen"],
                "group_size": 2,
                "timing_hint": "2 min per student, ~5 min total",
                "notes_for_teacher": "Walk around and listen for confusion patterns.",
            },
        },
        {
            "type_name": "worksheet",
            "description": (
                "Printable or digital scaffold (fill-in-the-blank, guided practice sheet, recap "
                "template)."
            ),
            "required_fields": ["file_url"],
            "optional_fields": ["instructions", "estimated_time_min", "materials_needed"],
            "example_content_json": {
                "file_url": "https://cdn.example.com/handouts/binary-search-recap.pdf",
                "instructions": "Complete sections 1 and 2. Circle anything unclear.",
                "estimated_time_min": 8,
                "materials_needed": ["worksheet printout", "pencil"],
            },
        },
        {
            "type_name": "video",
            "description": (
                "Short clip, animation, or walkthrough. Usually used for visual learners or calm "
                "focus."
            ),
            "required_fields": ["url"],
            "optional_fields": ["duration_sec", "notes", "pause_points"],
            "example_content_json": {
                "url": "https://youtube.com/watch?v=dQw4w9WgXcQ",
                "duration_sec": 180,
                "notes": "Focus on how pointers move in the array.",
                "pause_points": [
                    {
                        "timestamp_sec": 42,
                        "prompt": "What changed between left and right pointers?",
                    },
                    {"timestamp_sec": 95, "prompt": "Why does mid move here?"},
                ],
            },
        },
        {
            "type_name": "article",
            "description": "Short reading (article, blog post, mini explainer, summary notes).",
            "required_fields": ["url"],
            "optional_fields": ["reading_time_min", "key_points", "reflection_questions"],
            "example_content_json": {
                "url": "https://example.com/intro-to-hash-tables-explained-for-beginners",
                "reading_time_min": 5,
                "key_points": [
                    "Hash = fast lookup",
                    "Collisions happen, we resolve them",
                    "Real-world analogy: dictionary or phone book",
                ],
                "reflection_questions": [
                    "Which part felt confusing?",
                    "Where could you apply this concept?",
                ],
            },
        },
        {
            "type_name": "breathing-exercise",
            "description": (
                "Short guided calm/reset routine to regulate mood (good for 'sad', 'frustrated', "
                "'overwhelmed')."
            ),
            "required_fields": ["script_steps"],
            "optional_fields": ["duration_sec", "materials_needed", "notes_for_teacher"],
            "example_content_json": {
                "script_steps": [
                    "Breathe in slowly for 4 seconds.",
                    "Hold for 4 seconds.",
                    "Breathe out gently for 4 seconds.",
                    "Repeat 4 times.",
                    "Write down one thing that's still stressful.",
                ],
                "duration_sec": 60,
                "materials_needed": ["quiet space"],
                "notes_for_teacher": "You can say this script out loud or project it on screen.",
            },
        },
    ]

    activity_seed_data = [
        {
            "name": "Partner Teach-Back",
            "summary": "Students teach a concept to each other to reinforce learning.",
            "type": "in-class-task",
            "tags": ["pairwork", "active-learning", "communication"],
            "content_json": {
                "steps": [
                    "Pair up with someone near you.",
                    "Take turns explaining the main idea of today's topic.",
                    "Ask your partner one question about their explanation.",
                ],
                "materials_needed": ["timer", "whiteboard"],
                "group_size": 2,
                "timing_hint": "5 minutes total",
            },
        },
        {
            "name": "Binary Search Practice Sheet",
            "summary": "Guided worksheet for tracing binary search steps.",
            "type": "worksheet",
            "tags": ["algorithm", "visual", "practice"],
            "content_json": {
                "file_url": "https://cdn.example.com/handouts/binary-search.pdf",
                "instructions": "Trace the mid-index updates step by step.",
                "estimated_time_min": 10,
                "materials_needed": ["worksheet printout", "pencil"],
            },
        },
        {
            "name": "Binary Search Visualization",
            "summary": "Watch how the mid index moves in a visual demo.",
            "type": "video",
            "tags": ["visual", "algorithm", "demo"],
            "content_json": {
                "url": "https://youtube.com/watch?v=oev8jzBzI3A",
                "duration_sec": 210,
                "notes": "Pause halfway to predict where mid will move next.",
                "pause_points": [
                    {"timestamp_sec": 80, "prompt": "Predict the next mid index."},
                    {"timestamp_sec": 150, "prompt": "How many elements are left to search?"},
                ],
            },
        },
        {
            "name": "Intro to Hash Tables Article",
            "summary": "A beginner-friendly reading explaining hash table basics.",
            "type": "article",
            "tags": ["data-structure", "reading", "theory"],
            "content_json": {
                "url": "https://example.com/intro-hash-tables",
                "reading_time_min": 5,
                "key_points": [
                    "Hash functions map keys to indices.",
                    "Collisions are unavoidable but manageable.",
                    "Think of a hash table like a phone book.",
                ],
                "reflection_questions": [
                    "What is a hash collision?",
                    "Where might hashing be useful in daily software?",
                ],
            },
        },
        {
            "name": "Calm Reset Routine",
            "summary": "Short guided breathing exercise for stressed students.",
            "type": "breathing-exercise",
            "tags": ["mindfulness", "calm", "wellbeing", "__system_default__"],
            "content_json": {
                "script_steps": [
                    "Breathe in through your nose for 4 seconds.",
                    "Hold for 4 seconds.",
                    "Exhale through your mouth for 4 seconds.",
                    "Repeat 4 times.",
                    "Stretch your shoulders and refocus.",
                ],
                "duration_sec": 60,
                "materials_needed": ["quiet space"],
                "notes_for_teacher": "Optionally dim lights or play calm music.",
            },
        },
    ]

    existing_types = {row.type_name: row for row in db.query(ActivityType).all()}
    for entry in activity_type_seed_data:
        if entry["type_name"] in existing_types:
            print(f"ℹ️  Activity type already exists, skipping: {entry['type_name']}")
            continue
        db.add(ActivityType(**entry))
    db.commit()

    seed_creator = (
        {
            "creator_id": teacher.id,
            "creator_name": teacher.full_name or teacher.email,
            "creator_email": teacher.email,
        }
        if teacher
        else {
            "creator_id": None,
            "creator_name": "System Seed",
            "creator_email": "seed@system.local",
        }
    )

    existing_activities = {row.name: row for row in db.query(Activity).all()}
    created: Dict[str, Activity] = {}
    for entry in activity_seed_data:
        payload = {**entry, **seed_creator}
        if payload["name"] in existing_activities:
            print(f"ℹ️  Activity already exists, skipping: {payload['name']}")
            created[payload["name"]] = existing_activities[payload["name"]]
            continue
        activity = Activity(**payload)
        db.add(activity)
        db.flush()
        created[payload["name"]] = activity

    db.commit()
    print("🎯 Default activity types & example activities ensured.")
    system_default_name = "Calm Reset Routine"
    system_default = created.get(system_default_name) or existing_activities.get(
        system_default_name
    )
    if system_default:
        tags = list(system_default.tags or [])
        if "__system_default__" not in tags:
            tags.append("__system_default__")
            system_default.tags = tags
            db.add(system_default)
            db.commit()
    return created


def create_recommendations(
    db: Session,
    course: Course,
    activities: Dict[str, Activity],
) -> None:
    """Map learning styles + moods to activities."""
    name_lookup = activities
    recommendation_specs = [
        ("Active learner", None, "Partner Teach-Back"),
        ("Structured learner", None, "Binary Search Practice Sheet"),
        ("Passive learner", None, "Calm Reset Routine"),
        (None, "worried", "Calm Reset Routine"),
        (None, "energized", "Binary Search Visualization"),
        (None, "steady", "Intro to Hash Tables Article"),
    ]

    existing_map = {
        (rec.learning_style, rec.mood): rec
        for rec in db.query(CourseRecommendation).filter_by(course_id=course.id).all()
    }

    recommendations: List[CourseRecommendation] = []
    for learning_style, mood, activity_name in recommendation_specs:
        activity = name_lookup.get(activity_name)
        if not activity:
            print(
                f"⚠️  Skipping recommendation for '{activity_name}' because activity was not seeded."
            )
            continue
        key = (learning_style, mood)
        if key in existing_map:
            print(f"ℹ️  Recommendation already exists for course {course.title}: {key}, skipping.")
            continue
        recommendations.append(
            CourseRecommendation(
                course_id=course.id,
                learning_style=learning_style,
                mood=mood,
                activity_id=activity.id,
            )
        )
    for rec in recommendations:
        db.add(rec)
    db.flush()
    print("💡 Course recommendations configured.")


def create_sessions(
    db: Session,
    course: Course,
    baseline: SurveyTemplate,
) -> List[ClassSession]:
    snapshot = build_survey_snapshot(baseline)
    mood_schema = {"prompt": "How are you feeling today?", "options": course.mood_labels or []}

    rebaseline_session = ClassSession(
        id=str(uuid.uuid4()),
        course_id=course.id,
        survey_template_id=baseline.id,
        require_survey=True,
        mood_check_schema=mood_schema,
        survey_snapshot_json=snapshot,
        join_token=uuid.uuid4().hex[:12],
    )

    followup_session = ClassSession(
        id=str(uuid.uuid4()),
        course_id=course.id,
        survey_template_id=baseline.id,
        require_survey=False,
        mood_check_schema=mood_schema,
        survey_snapshot_json=None,
        join_token=uuid.uuid4().hex[:12],
    )

    db.add_all([rebaseline_session, followup_session])
    course.requires_rebaseline = False
    db.flush()
    print("🗓️ Sessions created (baseline + follow-up).")
    return [rebaseline_session, followup_session]


def create_submissions_and_profiles(
    db: Session,
    course: Course,
    sessions: List[ClassSession],
    students: List[Student],
) -> None:
    baseline_session, followup_session = sessions
    student = students[0]

    # Baseline submission (requires survey).
    baseline_answers = {
        "q1": "5 — Yes, a lot",
        "q2": "5 — Yes, a lot",
        "q3": "3 — Not sure",
        "q4": "3 — Not sure",
        "q5": "2 — Low",
        "q6": "2 — A little worried",
        "q7": "A —  Move break",
        "q8": "A — Try it with hands/body",
        "q9": "A — Quick game / movement challenge",
    }
    totals = compute_total_scores(baseline_session.survey_snapshot_json or {}, baseline_answers)
    learning_style = determine_learning_style(totals) or "Active learner"

    baseline_submission = Submission(
        id=str(uuid.uuid4()),
        session_id=baseline_session.id,
        course_id=course.id,
        student_id=student.id,
        mood="energized",
        answers_json=baseline_answers,
        total_scores=totals,
        is_baseline_update=True,
        status="completed",
    )
    db.add(baseline_submission)
    db.flush()

    profile = CourseStudentProfile(
        id=str(uuid.uuid4()),
        course_id=course.id,
        student_id=student.id,
        latest_submission_id=baseline_submission.id,
        profile_category=learning_style,
        profile_scores_json=totals,
        is_current=True,
    )
    db.add(profile)

    # Student 2 mood-only submission (no survey).
    followup_submission = Submission(
        id=str(uuid.uuid4()),
        session_id=followup_session.id,
        course_id=course.id,
        student_id=students[1].id,
        mood="steady",
        answers_json=None,
        total_scores=None,
        is_baseline_update=False,
        status="completed",
    )
    db.add(followup_submission)

    # Guest submission.
    guest_submission = Submission(
        id=str(uuid.uuid4()),
        session_id=followup_session.id,
        course_id=course.id,
        guest_name="Jordan (Guest)",
        guest_id=str(uuid.uuid4()),
        mood="worried",
        answers_json=None,
        total_scores=None,
        is_baseline_update=False,
        status="completed",
    )
    db.add(guest_submission)
    db.flush()
    print("📝 Submissions + profiles recorded.")


def seed_data() -> None:
    db = SessionLocal()
    try:
        print("🌱 Starting seed process…")
        reset_database(db)

        teacher = create_teacher(db)
        students = create_students(db)
        baseline_survey, extra_surveys = create_surveys(db, teacher)
        course = create_course(db, teacher, baseline_survey)
        activities = seed_default_activity_types_and_activities(db, teacher)
        create_recommendations(db, course, activities)
        sessions = create_sessions(db, course, baseline_survey)
        create_submissions_and_profiles(db, course, sessions, students)

        if extra_surveys:
            print(
                f"📚 Additional survey templates added: {', '.join(s.title for s in extra_surveys)}"
            )

        db.commit()
        print("🎉 Seed data inserted successfully!")
    except Exception as exc:  # pragma: no cover - debugging aid
        db.rollback()
        print(f"❌ Seed failed: {exc}")
        raise
    finally:
        db.close()


if __name__ == "__main__":
    seed_data()
