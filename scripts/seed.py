#!/usr/bin/env python3
"""
Seed script for 5500 Backend.
Creates sample data for development and testing.
"""

import sys
import uuid
from pathlib import Path

# Add the project root to Python path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

# Import after path setup
from app.core.security import hash_password  # noqa: E402
from app.db import Base, SessionLocal, engine  # noqa: E402
from app.models import ClassSession, Course, Submission, SurveyTemplate, Teacher  # noqa: E402


def create_tables() -> None:
    """Create all tables if they don't exist."""
    Base.metadata.create_all(bind=engine)


def seed_survey_templates() -> None:
    """Seed survey templates with 8 questions each."""
    db = SessionLocal()

    try:
        # Survey Template A: Learning Style Survey A
        template_a_questions = [
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

        # Survey Template B: Learning Style Survey B
        template_b_questions = [
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

        # Create Template A
        existing_a = (
            db.query(SurveyTemplate)
            .filter(SurveyTemplate.title == "Learning Style Survey A")
            .first()
        )
        if not existing_a:
            template_a = SurveyTemplate(
                title="Learning Style Survey A", questions_json=template_a_questions
            )
            db.add(template_a)
            print("✅ Created Learning Style Survey A")
        else:
            print("✅ Learning Style Survey A already exists")

        # Create Template B
        existing_b = (
            db.query(SurveyTemplate)
            .filter(SurveyTemplate.title == "Learning Style Survey B")
            .first()
        )
        if not existing_b:
            template_b = SurveyTemplate(
                title="Learning Style Survey B", questions_json=template_b_questions
            )
            db.add(template_b)
            print("✅ Created Learning Style Survey B")
        else:
            print("✅ Learning Style Survey B already exists")

        db.commit()
        print("🎉 Survey templates seeded successfully!")

    except Exception as e:
        print(f"❌ Error seeding survey templates: {e}")
        db.rollback()
        raise
    finally:
        db.close()


def seed_data() -> None:
    """Seed the database with sample data."""
    db = SessionLocal()

    try:
        # 1. Create Teacher
        print("Creating teacher...")
        teacher_email = "teacher1@example.com"
        existing_teacher = db.query(Teacher).filter(Teacher.email == teacher_email).first()

        if not existing_teacher:
            teacher = Teacher(
                id=uuid.uuid4(), email=teacher_email, password_hash=hash_password("Passw0rd!")
            )
            db.add(teacher)
            db.commit()
            db.refresh(teacher)
            print(f"✅ Created teacher: {teacher.email}")
        else:
            teacher = existing_teacher
            print(f"✅ Teacher already exists: {teacher.email}")

        # 2. Create Course
        print("Creating course...")
        course_title = "CS101 — Intro Class"
        existing_course = (
            db.query(Course)
            .filter(Course.teacher_id == teacher.id, Course.title == course_title)
            .first()
        )

        if not existing_course:
            course = Course(id=uuid.uuid4(), teacher_id=teacher.id, title=course_title)
            db.add(course)
            db.commit()
            db.refresh(course)
            print(f"✅ Created course: {course.title}")
        else:
            course = existing_course
            print(f"✅ Course already exists: {course.title}")

        # 3. Create Session A with fixed token
        print("Creating Session A...")
        session_a_token = "Ab3kZp7Q"
        existing_session_a = (
            db.query(ClassSession).filter(ClassSession.join_token == session_a_token).first()
        )

        if not existing_session_a:
            # Get a survey template to link
            template_a = (
                db.query(SurveyTemplate)
                .filter(SurveyTemplate.title == "Learning Style Survey A")
                .first()
            )
            if not template_a:
                raise Exception("Learning Style Survey A template not found for session seeding.")

            session_a = ClassSession(
                id=str(uuid.uuid4()),
                course_id=str(course.id),
                survey_template_id=str(template_a.id),
                join_token=session_a_token,
            )
            db.add(session_a)
            db.commit()
            db.refresh(session_a)
            print(f"✅ Created Session A with token: {session_a.join_token}")
        else:
            session_a = existing_session_a
            print(f"✅ Session A already exists with token: {session_a.join_token}")

        # 4. Create Session B with fixed token
        print("Creating Session B...")
        session_b_token = "Qx9Lm2Ta"
        existing_session_b = (
            db.query(ClassSession).filter(ClassSession.join_token == session_b_token).first()
        )

        if not existing_session_b:
            # Get a survey template to link
            template_b = (
                db.query(SurveyTemplate)
                .filter(SurveyTemplate.title == "Learning Style Survey B")
                .first()
            )
            if not template_b:
                raise Exception("Learning Style Survey B template not found for session seeding.")

            session_b = ClassSession(
                id=str(uuid.uuid4()),
                course_id=str(course.id),
                survey_template_id=str(template_b.id),
                join_token=session_b_token,
            )
            db.add(session_b)
            db.commit()
            db.refresh(session_b)
            print(f"✅ Created Session B with token: {session_b.join_token}")
        else:
            session_b = existing_session_b
            print(f"✅ Session B already exists with token: {session_b.join_token}")

        # 5. Create sample submissions for Session A
        print("Creating sample submissions...")
        submissions_data = [
            ("Alice", {"name": "Alice", "mood": "good"}),
            ("Bob", {"name": "Bob", "mood": "neutral"}),
        ]

        for student_name, answers in submissions_data:
            existing_submission = (
                db.query(Submission)
                .filter(
                    Submission.session_id == session_a.id, Submission.student_name == student_name
                )
                .first()
            )

            if not existing_submission:
                submission = Submission(
                    id=str(uuid.uuid4()),
                    session_id=str(session_a.id),
                    student_name=student_name,
                    answers_json=answers,
                )
                db.add(submission)
                print(f"✅ Created submission for {student_name}")
            else:
                print(f"✅ Submission already exists for {student_name}")

        db.commit()
        print("\n🎉 Seed data created successfully!")
        print(f"📧 Teacher email: {teacher_email}")
        print("🔑 Teacher password: Passw0rd!")
        print(f"🔗 Session A token: {session_a_token}")
        print(f"🔗 Session B token: {session_b_token}")

    except Exception as e:
        print(f"❌ Error seeding data: {e}")
        db.rollback()
        raise
    finally:
        db.close()


def main() -> None:
    """Main function to run the seed script."""
    print("🌱 Starting database seeding...")

    # Create tables
    create_tables()
    print("✅ Database tables created/verified")

    # Seed survey templates first
    print("📋 Seeding survey templates...")
    seed_survey_templates()

    # Seed other data
    seed_data()

    print("\n✨ Seeding complete!")


if __name__ == "__main__":
    main()
