import secrets
from typing import Any

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import and_, func
from sqlalchemy.orm import Session

from app.api.deps import get_current_teacher
from app.core.config import settings
from app.db import get_db
from app.models.class_session import ClassSession
from app.models.course import Course
from app.models.submission import Submission
from app.models.survey_template import SurveyTemplate
from app.models.teacher import Teacher
from app.schemas.session import SessionCloseOut, SessionCreate, SessionOut
from app.schemas.submission import SubmissionItem, SubmissionsOut

router = APIRouter()


@router.post("/{course_id}/sessions", response_model=SessionOut)
def create_session(
    course_id: str,
    session_data: SessionCreate,
    db: Session = Depends(get_db),
    current_teacher: Teacher = Depends(get_current_teacher),
) -> SessionOut:
    """Create a new session for a course."""
    # Verify course ownership
    course = (
        db.query(Course)
        .filter(and_(Course.id == course_id, Course.teacher_id == current_teacher.id))
        .first()
    )

    if not course:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="COURSE_NOT_FOUND")

    # Validate survey template exists
    template = (
        db.query(SurveyTemplate)
        .filter(SurveyTemplate.id == session_data.survey_template_id)
        .first()
    )
    if not template:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="SURVEY_TEMPLATE_NOT_FOUND"
        )

    # Generate unique join token
    join_token = secrets.token_urlsafe(10)

    # Create session
    session = ClassSession(
        course_id=course_id,
        survey_template_id=session_data.survey_template_id,
        join_token=join_token,
    )

    db.add(session)
    db.commit()
    db.refresh(session)

    # Build QR URL
    qr_url = f"{settings.public_app_url}/join?s={join_token}"

    survey_schema_data: list[dict[str, Any]] = template.questions_json or []  # type: ignore[assignment]
    assert isinstance(survey_schema_data, list)
    return SessionOut(
        session_id=str(session.id),
        course_id=str(session.course_id),
        started_at=session.started_at,  # type: ignore[arg-type]
        closed_at=session.closed_at,  # type: ignore[arg-type]
        join_token=str(session.join_token),
        qr_url=qr_url,
        survey_schema=survey_schema_data,
    )


@router.post("/{session_id}/close", response_model=SessionCloseOut)
def close_session(
    session_id: str,
    db: Session = Depends(get_db),
    current_teacher: Teacher = Depends(get_current_teacher),
) -> SessionCloseOut:
    """Close a session."""
    # Verify session ownership through course
    session = (
        db.query(ClassSession)
        .join(Course)
        .filter(and_(ClassSession.id == session_id, Course.teacher_id == current_teacher.id))
        .first()
    )

    if not session:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="SESSION_NOT_FOUND")

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
    # Verify session ownership through course
    session = (
        db.query(ClassSession)
        .join(Course)
        .filter(and_(ClassSession.id == session_id, Course.teacher_id == current_teacher.id))
        .first()
    )

    if not session:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="SESSION_NOT_FOUND")

    # Get submissions
    submissions = db.query(Submission).filter(Submission.session_id == session_id).all()

    items = []
    for sub in submissions:
        # Determine display name and student info
        student_name = None
        student_id = None
        student_full_name = None

        if sub.student_id:
            # Authenticated student submission
            student_id = str(sub.student_id)
            if sub.student:
                student_full_name = str(sub.student.full_name)
        else:
            # Guest submission
            student_name = str(sub.guest_name) if sub.guest_name else "Unknown"

        items.append(
            SubmissionItem(
                student_name=student_name,
                student_id=student_id,
                student_full_name=student_full_name,
                answers=dict(sub.answers_json) if sub.answers_json else {},
                total_scores=dict(sub.total_scores) if sub.total_scores else None,
                status=str(sub.status),
                created_at=sub.created_at,  # type: ignore[arg-type]
                updated_at=sub.updated_at,  # type: ignore[arg-type]
            )
        )

    return SubmissionsOut(session_id=session_id, count=len(items), items=items)
