#!/usr/bin/env python3
"""
Seed the database with the minimal deploy dataset.

This script clears existing demo data and then loads ONLY:
  • the two legacy survey templates
  • the deploy activity types
  • the selected activities linked to those types

All other tables remain empty (aside from schema) after seeding.
"""

from __future__ import annotations

import sys
import uuid
from pathlib import Path
from typing import Dict, List

from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker

# Allow importing the app package when running as a script.
project_root = Path(__file__).resolve().parent.parent
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))

from app.core.config import settings  # noqa: E402
from scripts import seed as base_seed  # noqa: E402

SQLALCHEMY_DATABASE_URL = settings.database_url
engine = create_engine(SQLALCHEMY_DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def seed_surveys(db: Session) -> None:
    """Insert the two legacy survey templates (Critter Quest then Learning Buddy)."""
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

    survey_specs = [
        {
            "title": "Critter Quest: Learning Adventure",
            "questions": survey_2_questions,
        },
        {
            "title": "Learning Buddy: Style Check",
            "questions": survey_1_questions,
        },
    ]

    existing = {row.title: row for row in db.query(base_seed.SurveyTemplate).all()}
    for spec in survey_specs:
        if spec["title"] in existing:
            print(f"ℹ️  Survey already exists, skipping: {spec['title']}")
            continue
        survey = base_seed.SurveyTemplate(
            id=str(uuid.uuid4()),
            title=spec["title"],
            questions_json=spec["questions"],
            creator_name="System Seed",
            creator_id=None,
            creator_email="seed@system.local",
        )
        db.add(survey)
        db.flush()
        print(f"📝 Survey added: {survey.title}")
    db.commit()


def seed_activity_types_and_activities(db: Session) -> Dict[str, base_seed.Activity]:
    """Insert deploy activity types and associated activities."""
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
            "type_name": "music",
            "description": (
                "Background audio or music track (usually instrumental, low-distraction). "
                "Used to support calm focus, emotional regulation, or a specific activity mood."
            ),
            "required_fields": ["url"],
            "optional_fields": ["duration_sec", "notes"],
            "example_content_json": {
                "url": "https://www.youtube.com/watch?v=kGhHPX_TaI0",
                "duration_sec": 10086,
                "notes": (
                    "Soft instrumental track with steady beat and no lyrics. "
                    "Play quietly during independent work or reflection time. "
                    "You can start/stop at any time based on class needs."
                ),
            },
        },
    ]

    activity_seed_data = [
        {
            "name": "5 Steps to Wellbeing Animation",
            "summary": (
                "Animated video outlining five steps to improve mental health and wellbeing."
            ),
            "type": "video",
            "tags": ["wellbeing", "mental-health"],
            "content_json": {
                "url": "https://www.youtube.com/watch?v=x6bz_ekkrYA",
                "duration_sec": 151,
                "notes": (
                    "5 Steps to Wellbeing Animation — animated video outlining five steps to "
                    "improve mental health and wellbeing. After watching, students can act out "
                    "one step (e.g., talking to a friend) and use flags: green = I'll do it, "
                    "yellow = maybe, red = not yet."
                ),
            },
        },
        {
            "name": "Wellbeing For Children: Confidence And Self-Esteem",
            "summary": "Animation about confidence, self-esteem, and wellbeing.",
            "type": "video",
            "tags": ["wellbeing", "mental-health", "confidence", "__system_default__"],
            "content_json": {
                "url": "https://www.youtube.com/watch?v=pdjaxS4ME2A",
                "duration_sec": 389,
                "notes": (
                    "Wellbeing For Children: Confidence And Self-Esteem — animation about "
                    "confidence, self-esteem and wellbeing. Students can role-play confident "
                    "vs. unconfident body language and use flags green/yellow/red for how "
                    "good the posture/behaviour is for wellbeing."
                ),
            },
        },
        {
            "name": "The Reflection in Me",
            "summary": "Short film about self-image and self-acceptance.",
            "type": "video",
            "tags": ["wellbeing", "mental-health"],
            "content_json": {
                "url": "https://www.youtube.com/watch?v=D9OOXCu5XMg",
                "duration_sec": 222,
                "notes": (
                    "The Reflection in Me — short about self-image and self-acceptance. "
                    "Students can complete a reflection (e.g., 'When I look in the mirror, "
                    "I feel…') and optionally use flags to show how they feel about themselves."
                ),
            },
        },
        {
            "name": "Music Track #1",
            "summary": "Calm, repetitive, no-lyrics background music.",
            "type": "music",
            "tags": ["music", "background", "calm", "focus"],
            "content_json": {
                "url": "https://www.youtube.com/watch?v=GR6AMEE43AI",
                "duration_sec": 36016,
                "notes": (
                    "Music Track #1 — calm, repetitive, no lyrics. Works as background music "
                    "for independent work or calming transitions, especially for students with "
                    "ADHD or attention challenges. You can start/stop at any time."
                ),
            },
        },
        {
            "name": "Music Track #2",
            "summary": "Soft, continuous melody with minimal volume changes.",
            "type": "music",
            "tags": ["music", "background", "calm"],
            "content_json": {
                "url": (
                    "https://www.youtube.com/watch?v=Dgjry2bhl9g&list=RDDgjry2bhl9g&start_radio=1"
                ),
                "duration_sec": 1516,
                "notes": (
                    "Music Track #2 — soft, continuous melody with minimal volume changes. "
                    "Good for emotional regulation and reducing anxiety while students work. "
                    "You can start/stop at any time."
                ),
            },
        },
        {
            "name": "Personal World Map",
            "summary": "Quickly sketch a map of your personal world showing 3-5 important places.",
            "type": "worksheet",
            "tags": [
                "unit-1",
                "map-your-world",
                "geography",
                "self-reflection",
                "solo",
                "visual",
                "creative",
                "active",
            ],
            "content_json": {
                "file_url": "http://localhost:8000/activity/personal-world-map.pdf",
                "instructions": (
                    "Draw a map of your personal world showing important places in your life.\n"
                    "1. Draw your home in the center of the map\n"
                    "2. Add your school\n"
                    "3. Add 1-3 other important places (park, friend's house, library,\n"
                    "   store, etc.)\n"
                    "4. Draw a compass rose showing North (N), South (S), East (E), and West (W)\n"
                    "5. Label each place clearly\n\n"
                    "Remember: This is YOUR world map - include places that matter to you!"
                ),
                "estimated_time_min": 5,
                "materials_needed": ["worksheet printout or blank paper", "pencil"],
            },
        },
        {
            "name": "Map Reading Practice",
            "summary": "Quick practice identifying map symbols and reading directions.",
            "type": "worksheet",
            "tags": [
                "unit-1",
                "map-your-world",
                "geography",
                "map-skills",
                "solo",
                "structured",
                "passive",
            ],
            "content_json": {
                "file_url": "http://localhost:8000/activity/map-reading-practice.pdf",
                "instructions": (
                    "Part 1: Match the symbol with its meaning (draw a line to connect)\n"
                    "[Symbol] 🏠 → House/Building\n"
                    "[Symbol] 🌳 → Park/Forest\n"
                    "[Symbol] 🛣️ → Road\n"
                    "[Symbol] 🏫 → School\n"
                    "[Symbol] 🏥 → Hospital\n\n"
                    "Part 2: Compass Directions\n"
                    "1. If you face North, which direction is to your right? __________\n"
                    "2. If you face South, which direction is behind you? __________\n"
                    "3. If you go East, then turn right, which direction are you facing? __________"
                ),
                "estimated_time_min": 5,
                "materials_needed": ["worksheet printout", "pencil"],
            },
        },
        {
            "name": "Body Systems Quick Check",
            "summary": "Quick review of major body systems.",
            "type": "worksheet",
            "tags": [
                "unit-3",
                "anatomy",
                "physiology",
                "body-systems",
                "solo",
                "structured",
                "passive",
            ],
            "content_json": {
                "file_url": "http://localhost:8000/activity/body-systems-quick-check.pdf",
                "instructions": (
                    "Part 1: Match the body system with its main function\n"
                    "1. Circulatory System    → A. Moves blood through the body\n"
                    "2. Respiratory System   → B. Takes in oxygen and removes carbon dioxide\n"
                    "3. Digestive System    → C. Breaks down food for energy\n"
                    "4. Nervous System      → D. Controls body functions and sends messages\n"
                    "5. Skeletal System     → E. Provides structure and support\n\n"
                    "Part 2: Which system works with the circulatory system to deliver oxygen?\n"
                    "Circle your answer: Respiratory System  /  Digestive System  /  Nervous System"
                ),
                "estimated_time_min": 5,
                "materials_needed": ["worksheet printout", "pencil"],
            },
        },
        {
            "name": "Body Systems Reading",
            "summary": "Read a short article about how body systems work together.",
            "type": "article",
            "tags": [
                "unit-3",
                "anatomy",
                "physiology",
                "reading",
                "solo",
                "passive",
                "structured",
            ],
            "content_json": {
                "url": "https://www.verywellhealth.com/organ-system-1298691",
                "reading_time_min": 3,
                "key_points": [
                    "The body has 11 major organ systems",
                    "Systems work together to maintain health",
                    "Example: circulatory and respiratory systems deliver oxygen",
                ],
                "reflection_questions": [
                    "Name two systems that work together. How?",
                ],
            },
        },
        {
            "name": "Quick Relationship Reflection",
            "summary": "Quick 5-minute reflection on your relationships.",
            "type": "in-class-task",
            "tags": [
                "unit-6",
                "relationships",
                "reflection",
                "solo",
                "structured",
                "passive",
            ],
            "content_json": {
                "steps": [
                    "List 3 important relationships in your life",
                    "Write one thing you appreciate about each relationship",
                    "Write one way you can strengthen one relationship this week",
                ],
                "materials_needed": ["paper", "pen or pencil"],
                "group_size": 1,
                "timing_hint": "5 minutes total",
                "notes_for_teacher": (
                    "This is a solo reflection activity. Students can work at their own pace."
                ),
            },
        },
    ]

    existing_types = {row.type_name: row for row in db.query(base_seed.ActivityType).all()}
    for entry in activity_type_seed_data:
        if entry["type_name"] in existing_types:
            print(f"ℹ️  Activity type already exists, skipping: {entry['type_name']}")
            continue
        db.add(base_seed.ActivityType(**entry))
    db.commit()

    seed_creator = {
        "creator_id": None,
        "creator_name": "System Seed",
        "creator_email": "seed@system.local",
    }

    existing_activities = {row.name: row for row in db.query(base_seed.Activity).all()}
    created: Dict[str, base_seed.Activity] = {}
    for entry in activity_seed_data:
        payload = {**entry, **seed_creator}
        if payload["name"] in existing_activities:
            print(f"ℹ️  Activity already exists, skipping: {payload['name']}")
            created[payload["name"]] = existing_activities[payload["name"]]
            continue
        activity = base_seed.Activity(**payload)
        db.add(activity)
        db.flush()
        created[payload["name"]] = activity

    db.commit()
    print("🎯 Deploy activity types & activities seeded.")

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
            print("⭐ Marked Calm Reset Routine as system default activity.")
    return created


def seed_data() -> None:
    db = SessionLocal()
    try:
        print("🌱 Starting deploy seed…")
        base_seed.reset_database(db)
        seed_surveys(db)
        seed_activity_types_and_activities(db)
        db.commit()
        print("🎉 Deploy dataset loaded successfully!")
    except Exception as exc:  # pragma: no cover - debugging aid
        db.rollback()
        print(f"❌ Seed failed: {exc}")
        raise
    finally:
        db.close()


if __name__ == "__main__":
    seed_data()
