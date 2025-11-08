import uuid
from typing import Dict, Optional

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session, joinedload

from app.api.deps import get_current_student_optional
from app.db import get_db
from app.models.class_session import ClassSession
from app.models.course import Course
from app.models.student import Student
from app.models.submission import Submission
from app.schemas.public import (
    PublicJoinOut,
    PublicSurveySnapshot,
    SubmissionIn,
    SubmissionOut,
    SubmissionStatusOut,
)
from app.schemas.recommendations import RecommendedActivityOut
from app.services.recommendations import (
    build_recommended_activity_payload,
    get_recommended_activity,
)
from app.services.submissions import (
    get_current_profile,
    update_course_student_profile,
    upsert_submission,
)
from app.services.surveys import (
    compute_total_scores,
    determine_learning_style,
    snapshot_to_public_payload,
)

router = APIRouter()


def _get_session_by_token(db: Session, join_token: str) -> ClassSession:
    session = (
        db.query(ClassSession)
        .options(joinedload(ClassSession.course))
        .filter(ClassSession.join_token == join_token)
        .first()
    )
    if not session:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="SESSION_NOT_FOUND")
    return session


def _ensure_session_open(session: ClassSession) -> None:
    if session.closed_at is not None:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="SESSION_CLOSED")


@router.get("/join/{join_token}", response_model=PublicJoinOut)
def public_session_info(join_token: str, db: Session = Depends(get_db)) -> PublicJoinOut:
    """Return public-facing session details for joining."""
    session = _get_session_by_token(db, join_token)
    _ensure_session_open(session)

    course = session.course
    if not course:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="COURSE_NOT_FOUND"
        )

    survey_payload = None
    if session.require_survey:
        survey_payload_dict = snapshot_to_public_payload(session.survey_snapshot_json)
        if survey_payload_dict:
            survey_payload = PublicSurveySnapshot.model_validate(survey_payload_dict)

    mood_schema = session.mood_check_schema or {"prompt": "", "options": []}

    return PublicJoinOut(
        session_id=str(session.id),
        course_id=str(course.id),
        course_title=str(course.title),
        require_survey=bool(session.require_survey),
        mood_check_schema=mood_schema,
        survey=survey_payload,
        status="OPEN",
    )


def _validate_mood(course: Course, mood: str) -> None:
    if course.mood_labels and mood not in course.mood_labels:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="INVALID_MOOD_LABEL",
        )


def _generate_guest_id(existing_guest_id: Optional[str]) -> str:
    return existing_guest_id or str(uuid.uuid4())


def _build_recommended_activity(
    db: Session,
    course_id: str,
    mood: str,
    learning_style: Optional[str],
) -> RecommendedActivityOut:
    match_type, activity = get_recommended_activity(db, course_id, mood, learning_style)
    payload = build_recommended_activity_payload(match_type, mood, learning_style, activity)
    return RecommendedActivityOut.model_validate(payload)


@router.post("/join/{join_token}/submit", response_model=SubmissionOut)
def public_submit(
    join_token: str,
    submission_data: SubmissionIn,
    db: Session = Depends(get_db),
    current_student: Optional[Student] = Depends(get_current_student_optional),
) -> SubmissionOut:
    """Accept mood and optional survey responses for a public session."""
    session = _get_session_by_token(db, join_token)
    _ensure_session_open(session)

    course = session.course
    if not course:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="COURSE_NOT_FOUND"
        )

    _validate_mood(course, submission_data.mood)

    is_guest_mode = submission_data.is_guest or current_student is None

    if is_guest_mode:
        guest_name = (submission_data.student_name or "").strip()
        if not guest_name:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="GUEST_NAME_REQUIRED",
            )
        guest_id = _generate_guest_id(submission_data.guest_id)
    else:
        guest_name = None
        guest_id = None

    if session.require_survey and not submission_data.answers:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="ANSWERS_REQUIRED",
        )

    answers: Optional[Dict[str, str]] = submission_data.answers or None
    total_scores: Optional[Dict[str, int]] = None
    learning_style: Optional[str] = None
    is_baseline_update = False

    if answers and session.require_survey:
        total_scores = compute_total_scores(session.survey_snapshot_json or {}, answers)
        learning_style = determine_learning_style(total_scores)
        is_baseline_update = learning_style is not None

    submission = upsert_submission(
        db=db,
        session=session,
        course=course,
        mood=submission_data.mood,
        answers=answers,
        total_scores=total_scores,
        is_baseline_update=is_baseline_update,
        student=current_student if not is_guest_mode else None,
        guest_id=guest_id if is_guest_mode else None,
        guest_name=guest_name if is_guest_mode else None,
    )
    db.flush()

    participant_learning_style = learning_style

    if is_baseline_update and learning_style and total_scores:
        update_course_student_profile(
            db=db,
            course=course,
            submission=submission,
            learning_style=learning_style,
            total_scores=total_scores,
            student=current_student if not is_guest_mode else None,
            guest_id=guest_id if is_guest_mode else None,
        )
    else:
        # Look up existing profile if no new baseline captured
        profile = get_current_profile(
            db=db,
            course_id=course.id,
            student_id=current_student.id if current_student and not is_guest_mode else None,
            guest_id=guest_id if is_guest_mode else None,
        )
        if profile:
            participant_learning_style = profile.profile_category

    db.commit()
    db.refresh(submission)

    recommended_activity = _build_recommended_activity(
        db, course.id, submission_data.mood, participant_learning_style
    )

    # Determine message based on scenario
    if is_baseline_update:
        message = "Thanks! Your style for this course has been updated."
    elif participant_learning_style is None:
        # Scenario B2: No profile yet, only mood recorded
        message = "Thanks! Mood recorded. We'll learn your style next time we run the survey."
    else:
        # Scenario B1: Has existing profile, just recording mood
        message = "Thanks for checking in!"

    return SubmissionOut(
        submission_id=str(submission.id),
        student_id=str(submission.student_id) if submission.student_id else None,
        guest_id=str(submission.guest_id) if submission.guest_id else None,
        require_survey=bool(session.require_survey),
        is_baseline_update=is_baseline_update,
        mood=submission_data.mood,
        learning_style=participant_learning_style,
        total_scores=total_scores,
        recommended_activity=recommended_activity,
        message=message,
    )


@router.get("/join/{join_token}/submission", response_model=SubmissionStatusOut)
def get_submission_status(
    join_token: str,
    guest_id: Optional[str] = None,
    db: Session = Depends(get_db),
    current_student: Optional[Student] = Depends(get_current_student_optional),
) -> SubmissionStatusOut:
    """Check if a participant has already submitted for this session."""
    session = _get_session_by_token(db, join_token)
    _ensure_session_open(session)

    # Check if submission exists for guest or student
    query = db.query(Submission).filter(Submission.session_id == session.id)

    if current_student:
        query = query.filter(Submission.student_id == current_student.id)
    elif guest_id:
        query = query.filter(Submission.guest_id == guest_id)
    else:
        # No identifier provided
        return SubmissionStatusOut(submitted=False)

    submission = query.first()
    return SubmissionStatusOut(submitted=submission is not None)
