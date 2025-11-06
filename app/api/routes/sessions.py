import secrets
from collections import Counter
from typing import Any, Dict, List, Optional

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import and_, func
from sqlalchemy.orm import Session, joinedload

from app.api.deps import get_current_teacher
from app.core.config import settings
from app.db import get_db
from app.models.class_session import ClassSession
from app.models.course import Course
from app.models.course_student_profile import CourseStudentProfile
from app.models.submission import Submission
from app.models.survey_template import SurveyTemplate
from app.models.teacher import Teacher
from app.schemas.recommendations import RecommendedActivityOut
from app.schemas.session import (
    SessionCloseOut,
    SessionCreate,
    SessionDashboardOut,
    SessionDashboardParticipant,
    SessionOut,
)
from app.schemas.submission import SubmissionItem, SubmissionsOut
from app.services.recommendations import (
    build_recommended_activity_payload,
    get_recommended_activity,
)
from app.services.surveys import build_survey_snapshot, determine_learning_style

router = APIRouter()


def _get_course_for_teacher(db: Session, course_id: str, teacher: Teacher) -> Course:
    course = (
        db.query(Course)
        .filter(and_(Course.id == course_id, Course.teacher_id == teacher.id))
        .first()
    )
    if not course:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="COURSE_NOT_FOUND")
    return course


def _get_session_for_teacher(
    db: Session,
    session_id: str,
    teacher: Teacher,
    *,
    include_course: bool = False,
) -> ClassSession:
    query = (
        db.query(ClassSession)
        .join(Course, ClassSession.course_id == Course.id)
        .filter(and_(ClassSession.id == session_id, Course.teacher_id == teacher.id))
    )
    if include_course:
        query = query.options(joinedload(ClassSession.course))

    session = query.first()
    if not session:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="SESSION_NOT_FOUND")
    return session


def _load_baseline_template(db: Session, course: Course) -> SurveyTemplate:
    if not course.baseline_survey_id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="COURSE_BASELINE_NOT_SET",
        )
    template = (
        db.query(SurveyTemplate).filter(SurveyTemplate.id == course.baseline_survey_id).first()
    )
    if not template:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="SURVEY_TEMPLATE_NOT_FOUND",
        )
    return template


def _serialize_submission(submission: Submission) -> SubmissionItem:
    answers = submission.answers_json if submission.answers_json else None
    total_scores = submission.total_scores if submission.total_scores else None
    learning_style = None
    if total_scores:
        learning_style = determine_learning_style(
            {key: int(value) for key, value in total_scores.items()}
        )
    return SubmissionItem(
        student_name=submission.guest_name if submission.guest_id else None,
        student_id=str(submission.student_id) if submission.student_id else None,
        student_full_name=(
            str(submission.student.full_name)
            if submission.student and submission.student.full_name
            else None
        ),
        mood=str(submission.mood),
        answers=dict(answers) if answers else None,
        total_scores=dict(total_scores) if total_scores else None,
        learning_style=learning_style,
        is_baseline_update=bool(submission.is_baseline_update),
        status=str(submission.status),
        created_at=submission.created_at,  # type: ignore[arg-type]
        updated_at=submission.updated_at,  # type: ignore[arg-type]
    )


def _build_recommended_activity_schema(
    db: Session,
    course_id: str,
    mood: str,
    learning_style: Optional[str],
) -> RecommendedActivityOut:
    match_type, activity = get_recommended_activity(db, course_id, mood, learning_style)
    payload = build_recommended_activity_payload(match_type, mood, learning_style, activity)
    return RecommendedActivityOut.model_validate(payload)


def _session_to_schema(session: ClassSession) -> SessionOut:
    """Serialize a session with the computed join QR URL."""
    qr_url = f"{settings.public_app_url}/join?s={session.join_token}"
    return SessionOut(
        session_id=str(session.id),
        course_id=str(session.course_id),
        require_survey=bool(session.require_survey),
        mood_check_schema=session.mood_check_schema or {"prompt": "", "options": []},
        survey_snapshot_json=session.survey_snapshot_json,
        started_at=session.started_at,  # type: ignore[arg-type]
        closed_at=session.closed_at,  # type: ignore[arg-type]
        join_token=session.join_token,
        qr_url=qr_url,
    )


@router.get("/{course_id}/sessions", response_model=List[SessionOut])
def list_course_sessions(
    course_id: str,
    db: Session = Depends(get_db),
    current_teacher: Teacher = Depends(get_current_teacher),
) -> List[SessionOut]:
    """List all sessions for a course."""
    course = _get_course_for_teacher(db, course_id, current_teacher)
    sessions = (
        db.query(ClassSession)
        .filter(ClassSession.course_id == course.id)
        .order_by(ClassSession.started_at.desc())
        .all()
    )
    return [_session_to_schema(session) for session in sessions]


@router.post(
    "/{course_id}/sessions", response_model=SessionOut, status_code=status.HTTP_201_CREATED
)
def create_session(
    course_id: str,
    session_data: SessionCreate,
    db: Session = Depends(get_db),
    current_teacher: Teacher = Depends(get_current_teacher),
) -> SessionOut:
    """Create a new session for a course."""
    course = _get_course_for_teacher(db, course_id, current_teacher)

    requested_require_survey = bool(session_data.require_survey)
    final_require_survey = course.requires_rebaseline or requested_require_survey

    if not course.mood_labels:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="COURSE_MOOD_LABELS_NOT_CONFIGURED",
        )

    survey_template: Optional[SurveyTemplate] = None
    survey_snapshot: Optional[Dict[str, Any]] = None
    if final_require_survey:
        survey_template = _load_baseline_template(db, course)
        survey_snapshot = build_survey_snapshot(survey_template)

    join_token = secrets.token_urlsafe(12)[:16]

    raw_prompt = session_data.mood_prompt.strip() if session_data.mood_prompt else ""
    mood_prompt = raw_prompt or "How are you feeling today?"

    session = ClassSession(
        course_id=course.id,
        survey_template_id=survey_template.id if survey_template else course.baseline_survey_id,
        require_survey=final_require_survey,
        mood_check_schema={
            "prompt": mood_prompt,
            "options": list(course.mood_labels or []),
        },
        survey_snapshot_json=survey_snapshot,
        join_token=join_token,
    )

    db.add(session)
    course.requires_rebaseline = False if final_require_survey else course.requires_rebaseline
    db.commit()
    db.refresh(session)
    db.refresh(course)

    return _session_to_schema(session)


@router.post("/{session_id}/close", response_model=SessionCloseOut)
def close_session(
    session_id: str,
    db: Session = Depends(get_db),
    current_teacher: Teacher = Depends(get_current_teacher),
) -> SessionCloseOut:
    """Close a session."""
    session = _get_session_for_teacher(db, session_id, current_teacher)
    if session.closed_at is not None:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="SESSION_ALREADY_CLOSED"
        )
    session.closed_at = func.now()  # type: ignore[assignment]
    db.commit()
    return SessionCloseOut(status="CLOSED")


@router.get("/{session_id}/submissions", response_model=SubmissionsOut)
def get_session_submissions(
    session_id: str,
    db: Session = Depends(get_db),
    current_teacher: Teacher = Depends(get_current_teacher),
) -> SubmissionsOut:
    """Get all submissions for a session."""
    session = _get_session_for_teacher(db, session_id, current_teacher)

    submissions = (
        db.query(Submission)
        .filter(Submission.session_id == session.id)
        .options(joinedload(Submission.student))
        .order_by(Submission.created_at.asc())
        .all()
    )

    items = [_serialize_submission(submission) for submission in submissions]
    return SubmissionsOut(session_id=session_id, count=len(items), items=items)


@router.get("/{session_id}/dashboard", response_model=SessionDashboardOut)
def get_session_dashboard(
    session_id: str,
    db: Session = Depends(get_db),
    current_teacher: Teacher = Depends(get_current_teacher),
) -> SessionDashboardOut:
    """Return session dashboard with participant mood and recommendations."""
    session = _get_session_for_teacher(db, session_id, current_teacher, include_course=True)
    course = session.course
    if not course:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="COURSE_NOT_FOUND"
        )

    submissions = (
        db.query(Submission)
        .filter(Submission.session_id == session.id)
        .options(joinedload(Submission.student))
        .all()
    )

    profiles = (
        db.query(CourseStudentProfile)
        .filter(
            CourseStudentProfile.course_id == course.id,
            CourseStudentProfile.is_current.is_(True),
        )
        .all()
    )
    profiles_by_student = {
        profile.student_id: profile for profile in profiles if profile.student_id
    }
    profiles_by_guest = {profile.guest_id: profile for profile in profiles if profile.guest_id}

    mood_counter: Counter[str] = Counter()
    participants: List[SessionDashboardParticipant] = []

    for submission in submissions:
        mood = submission.mood or "unknown"
        mood_counter[mood] += 1

        if submission.student_id:
            profile = profiles_by_student.get(submission.student_id)
            learning_style = profile.profile_category if profile else None
            display_name = submission.student.full_name if submission.student else "Student"
            participant = SessionDashboardParticipant(
                display_name=display_name,
                mode="student",
                student_id=str(submission.student_id),
                guest_id=None,
                mood=mood,
                learning_style=learning_style,
                recommended_activity=_build_recommended_activity_schema(
                    db, course.id, mood, learning_style
                ),
            )
        else:
            profile = profiles_by_guest.get(submission.guest_id)
            learning_style = profile.profile_category if profile else None
            display_name = submission.guest_name or "Guest"
            participant = SessionDashboardParticipant(
                display_name=display_name,
                mode="guest",
                student_id=None,
                guest_id=str(submission.guest_id) if submission.guest_id else None,
                mood=mood,
                learning_style=learning_style,
                recommended_activity=_build_recommended_activity_schema(
                    db, course.id, mood, learning_style
                ),
            )

        participants.append(participant)

    return SessionDashboardOut(
        session_id=str(session.id),
        course_id=str(course.id),
        course_title=str(course.title),
        require_survey=bool(session.require_survey),
        mood_summary=dict(mood_counter),
        participants=participants,
    )
