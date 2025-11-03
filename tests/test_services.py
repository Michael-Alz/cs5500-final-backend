"""Unit tests for service-layer helpers."""

from __future__ import annotations

import uuid

import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker

from app.models import (  # noqa: E402
    Activity,
    ActivityType,
    Base,
    ClassSession,
    Course,
    CourseRecommendation,
    CourseStudentProfile,
    Student,
    Teacher,
)
from app.services.recommendations import (  # noqa: E402
    build_recommended_activity_payload,
    ensure_defaults_for_course,
    get_recommended_activity,
    pick_system_default_activity,
)
from app.services.submissions import (  # noqa: E402
    get_current_profile,
    update_course_student_profile,
    upsert_submission,
)
from app.services.surveys import (  # noqa: E402
    compute_total_scores,
    determine_learning_style,
    extract_learning_style_categories,
    snapshot_to_public_payload,
)


# ---------------------------------------------------------------- Fixtures
@pytest.fixture()
def db_session() -> Session:
    engine = create_engine("sqlite:///:memory:", future=True)
    surveys_table = Base.metadata.tables.get("surveys")
    if surveys_table is not None:
        for idx in list(surveys_table.indexes):
            if idx.name == "ix_surveys_title":
                surveys_table.indexes.remove(idx)
    Base.metadata.drop_all(engine)
    Base.metadata.create_all(engine)
    SessionLocal = sessionmaker(bind=engine, expire_on_commit=False)
    session = SessionLocal()
    try:
        yield session
    finally:
        session.close()


# ---------------------------------------------------------------- Surveys helpers
def test_extract_learning_style_categories() -> None:
    questions = [
        {
            "id": "q1",
            "options": [
                {"scores": {"Visual": 2, "Auditory": 1}},
                {"scores": {"Kinesthetic": 3}},
            ],
        }
    ]
    categories = extract_learning_style_categories(questions)
    assert categories == ["Auditory", "Kinesthetic", "Visual"]


def test_compute_total_scores_and_determine_learning_style() -> None:
    snapshot = {
        "questions": [
            {
                "id": "q1",
                "options": [
                    {"id": "opt1", "scores": {"Visual": 2}},
                    {"id": "opt2", "scores": {"Auditory": 1}},
                ],
            },
            {
                "id": "q2",
                "options": [
                    {"label": "A", "scores": {"Visual": 1}},
                    {"label": "B", "scores": {"Auditory": 3}},
                ],
            },
        ]
    }
    answers = {"q1": "opt1", "q2": "B"}
    totals = compute_total_scores(snapshot, answers)
    assert totals == {"Visual": 2, "Auditory": 3}
    assert determine_learning_style(totals) == "Auditory"


def test_snapshot_to_public_payload() -> None:
    snapshot = {
        "survey_id": "survey-123",
        "title": "Sample",
        "questions": [
            {
                "id": "q1",
                "text": "Question?",
                "options": [{"label": "Yes"}, {"label": "No"}],
            }
        ],
    }
    public_payload = snapshot_to_public_payload(snapshot)
    assert public_payload["survey_id"] == "survey-123"
    assert public_payload["questions"][0]["options"][0]["text"] == "Yes"


# ---------------------------------------------------------------- Recommendation helpers
def _seed_recommendation_data(session: Session) -> tuple[Course, dict[str, Activity]]:
    teacher = Teacher(id="t1", email="t1@example.com", password_hash="hash", full_name="T1")
    session.add(teacher)

    course = Course(
        id="course1",
        title="Course",
        teacher_id=teacher.id,
        learning_style_categories=["Visual", "Auditory"],
        mood_labels=["happy", "sad"],
    )
    session.add(course)

    a_type = ActivityType(
        type_name="test-type",
        description="",
        required_fields=["steps"],
        optional_fields=[],
        example_content_json={},
    )
    session.add(a_type)
    session.flush()

    activities = {}
    for name in ["Exact", "StyleDefault", "MoodDefault", "Fallback"]:
        activity = Activity(
            id=f"act-{name.lower()}",
            name=name,
            summary=name,
            type=a_type.type_name,
            tags=[],
            content_json={"steps": ["one"]},
            creator_id=teacher.id,
            creator_name="T1",
            creator_email="t1@example.com",
        )
        session.add(activity)
        activities[name] = activity

    session.flush()

    mappings = [
        CourseRecommendation(
            course_id=course.id,
            learning_style="Visual",
            mood="happy",
            activity_id=activities["Exact"].id,
        ),
        CourseRecommendation(
            course_id=course.id,
            learning_style="Visual",
            mood=None,
            activity_id=activities["StyleDefault"].id,
        ),
        CourseRecommendation(
            course_id=course.id,
            learning_style=None,
            mood="sad",
            activity_id=activities["MoodDefault"].id,
        ),
        CourseRecommendation(
            course_id=course.id,
            learning_style=None,
            mood=None,
            activity_id=activities["Fallback"].id,
        ),
    ]
    session.add_all(mappings)
    session.commit()
    return course, activities


def _setup_course_with_activities(session: Session) -> tuple[Course, dict[str, Activity]]:
    teacher = Teacher(
        id=str(uuid.uuid4()),
        email="helper@example.com",
        password_hash="hash",
        full_name="Helper",
    )
    course = Course(
        id=str(uuid.uuid4()),
        title="Helper Course",
        teacher_id=teacher.id,
        learning_style_categories=["Visual", "Auditory"],
        mood_labels=["happy", "calm"],
    )
    activity_type = ActivityType(
        type_name=f"type-{uuid.uuid4().hex}",
        description="Helper type",
        required_fields=[],
        optional_fields=[],
        example_content_json={},
    )
    session.add_all([teacher, course, activity_type])
    session.flush()

    activities: dict[str, Activity] = {}

    def _make_activity(key: str, tags: list[str]) -> None:
        activity = Activity(
            id=str(uuid.uuid4()),
            name=f"{key.title()} Activity",
            summary=f"{key} summary",
            type=activity_type.type_name,
            tags=tags,
            content_json={"steps": ["one"]},
            creator_id=teacher.id,
            creator_name=teacher.full_name or teacher.email,
            creator_email=teacher.email,
        )
        session.add(activity)
        activities[key] = activity

    _make_activity("system", ["__system_default__", "core"])
    _make_activity("precise", ["class"])
    _make_activity("manual", ["manual"])

    session.commit()
    return course, activities


def test_get_recommended_activity_priority(db_session: Session) -> None:
    course, activities = _seed_recommendation_data(db_session)

    match, activity = get_recommended_activity(
        db_session, course.id, mood="happy", learning_style="Visual"
    )
    assert match == "style+mood"
    assert activity.id == activities["Exact"].id

    match, activity = get_recommended_activity(
        db_session, course.id, mood="neutral", learning_style="Visual"
    )
    assert match == "style-default"
    assert activity.id == activities["StyleDefault"].id

    match, activity = get_recommended_activity(
        db_session, course.id, mood="sad", learning_style="Unknown"
    )
    assert match == "mood-default"
    assert activity.id == activities["MoodDefault"].id

    match, activity = get_recommended_activity(
        db_session, course.id, mood="neutral", learning_style="Unknown"
    )
    assert match == "random-course-activity"
    assert activity is not None

    # Remove all recommendations -> fallback "none"
    db_session.query(CourseRecommendation).filter_by(course_id=course.id).delete()
    db_session.commit()
    match, activity = get_recommended_activity(
        db_session, course.id, mood="any", learning_style=None
    )
    default_activity = pick_system_default_activity(db_session)
    if default_activity:
        assert match == "system-default"
        assert activity is not None
        assert activity.id == default_activity.id
    else:
        assert match == "none"
        assert activity is None


def test_ensure_defaults_creates_global_default(db_session: Session) -> None:
    course, activities = _setup_course_with_activities(db_session)
    ensure_defaults_for_course(db_session, course.id, [])
    db_session.commit()

    global_default = (
        db_session.query(CourseRecommendation)
        .filter_by(course_id=course.id, learning_style=None, mood=None)
        .one()
    )
    assert global_default.is_auto is True
    assert global_default.activity_id == activities["system"].id


def test_ensure_defaults_creates_mood_and_style_defaults(db_session: Session) -> None:
    course, activities = _setup_course_with_activities(db_session)
    precise = CourseRecommendation(
        course_id=course.id,
        learning_style="Visual",
        mood="happy",
        activity_id=activities["precise"].id,
        is_auto=False,
    )
    db_session.add(precise)
    db_session.commit()

    ensure_defaults_for_course(
        db_session, course.id, [("Visual", "happy", activities["precise"].id)]
    )
    db_session.commit()

    mood_default = (
        db_session.query(CourseRecommendation)
        .filter_by(course_id=course.id, learning_style=None, mood="happy")
        .one()
    )
    assert mood_default.is_auto is True
    assert mood_default.activity_id == activities["precise"].id

    style_default = (
        db_session.query(CourseRecommendation)
        .filter_by(course_id=course.id, learning_style="Visual", mood=None)
        .one()
    )
    assert style_default.is_auto is True
    assert style_default.activity_id == activities["precise"].id


def test_ensure_defaults_respects_manual_defaults(db_session: Session) -> None:
    course, activities = _setup_course_with_activities(db_session)
    manual_default = CourseRecommendation(
        course_id=course.id,
        learning_style=None,
        mood="happy",
        activity_id=activities["manual"].id,
        is_auto=False,
    )
    precise = CourseRecommendation(
        course_id=course.id,
        learning_style="Visual",
        mood="happy",
        activity_id=activities["precise"].id,
        is_auto=False,
    )
    db_session.add_all([manual_default, precise])
    db_session.commit()

    ensure_defaults_for_course(
        db_session, course.id, [("Visual", "happy", activities["precise"].id)]
    )
    db_session.commit()
    db_session.refresh(manual_default)

    assert manual_default.activity_id == activities["manual"].id

    style_default = (
        db_session.query(CourseRecommendation)
        .filter_by(course_id=course.id, learning_style="Visual", mood=None)
        .one()
    )
    assert style_default.is_auto is True
    assert style_default.activity_id == activities["precise"].id


def test_build_recommended_activity_payload() -> None:
    payload = build_recommended_activity_payload("style+mood", "happy", "Visual", None)
    assert payload == {
        "match_type": "style+mood",
        "learning_style": "Visual",
        "mood": "happy",
        "activity": None,
    }


# ---------------------------------------------------------------- Submission helpers
def _seed_submission_context(session: Session) -> tuple[Course, ClassSession, Student]:
    teacher = Teacher(id="teacher1", email="t@example.com", password_hash="hash", full_name="T")
    course = Course(
        id="course1",
        title="Course",
        teacher_id=teacher.id,
        learning_style_categories=["Visual"],
        mood_labels=["happy", "neutral"],
    )
    session.add_all([teacher, course])

    session_obj = ClassSession(
        id="session1",
        course_id=course.id,
        require_survey=True,
        mood_check_schema={"prompt": "How?", "options": ["happy", "neutral"]},
        survey_snapshot_json={"questions": []},
        join_token="token",
    )
    session.add(session_obj)

    student = Student(
        id="student1", email="s@example.com", full_name="Student", password_hash="hash"
    )
    session.add(student)
    session.commit()
    return course, session_obj, student


def test_upsert_submission_creates_and_updates(db_session: Session) -> None:
    course, session_obj, student = _seed_submission_context(db_session)

    submission = upsert_submission(
        db_session,
        session=session_obj,
        course=course,
        mood="happy",
        answers={"q1": "opt"},
        total_scores={"Visual": 3},
        is_baseline_update=True,
        student=student,
    )
    db_session.commit()
    original_id = submission.id
    assert submission.mood == "happy"
    assert submission.total_scores == {"Visual": 3}

    # Update same participant; ensure same record reused
    submission = upsert_submission(
        db_session,
        session=session_obj,
        course=course,
        mood="neutral",
        answers=None,
        total_scores=None,
        is_baseline_update=False,
        student=student,
    )
    db_session.commit()
    assert submission.id == original_id
    assert submission.mood == "neutral"
    assert submission.answers_json is None
    assert submission.is_baseline_update is False


def test_update_course_student_profile_toggles_current(db_session: Session) -> None:
    course, session_obj, student = _seed_submission_context(db_session)

    submission = upsert_submission(
        db_session,
        session=session_obj,
        course=course,
        mood="happy",
        answers=None,
        total_scores={"Visual": 5},
        is_baseline_update=True,
        student=student,
    )
    db_session.commit()

    # Seed previous profile marked current
    old_profile = CourseStudentProfile(
        id="profile1",
        course_id=course.id,
        student_id=student.id,
        latest_submission_id=None,
        profile_category="Visual",
        profile_scores_json={"Visual": 2},
        is_current=True,
    )
    db_session.add(old_profile)
    db_session.commit()

    new_profile = update_course_student_profile(
        db_session,
        course=course,
        submission=submission,
        learning_style="Visual",
        total_scores={"Visual": 5},
        student=student,
    )
    db_session.commit()

    # Old profile should be marked not current, new one current
    db_session.refresh(old_profile)
    assert old_profile.is_current is False
    assert new_profile.is_current is True
    assert get_current_profile(db_session, course.id, student_id=student.id) == new_profile
