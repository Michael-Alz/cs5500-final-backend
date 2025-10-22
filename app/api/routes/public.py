from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import and_
from sqlalchemy.orm import Session

from app.db import get_db
from app.models.class_session import ClassSession
from app.models.submission import Submission
from app.models.survey_template import SurveyTemplate
from app.schemas.public import PublicJoinOut, SubmissionIn, SubmissionOut
from app.schemas.submission import SubmissionItem, SubmissionsOut

router = APIRouter()


@router.get("/join/{join_token}", response_model=PublicJoinOut)
def get_session_by_token(join_token: str, db: Session = Depends(get_db)) -> PublicJoinOut:
    """Get session information by join token."""
    session = db.query(ClassSession).filter(ClassSession.join_token == join_token).first()

    if not session:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="SESSION_NOT_FOUND")

    if session.closed_at is not None:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="SESSION_CLOSED")

    # Get survey template
    template = (
        db.query(SurveyTemplate).filter(SurveyTemplate.id == session.survey_template_id).first()
    )
    if not template:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="SURVEY_TEMPLATE_NOT_FOUND"
        )

    return PublicJoinOut(
        session_id=str(session.id),
        course_title=str(session.course.title),
        survey_schema=template.questions_json or [],
        status="OPEN" if session.closed_at is None else "CLOSED",
    )


@router.post("/join/{join_token}/submit", response_model=SubmissionOut)
def submit_survey(
    join_token: str, submission_data: SubmissionIn, db: Session = Depends(get_db)
) -> SubmissionOut:
    """Submit a survey response."""
    # Find session by token
    session = db.query(ClassSession).filter(ClassSession.join_token == join_token).first()

    if not session:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="SESSION_NOT_FOUND")

    if session.closed_at is not None:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="SESSION_CLOSED")

    # Validate submission data
    if not submission_data.student_name.strip():
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="VALIDATION_ERROR")

    # Check for duplicate submission
    existing_submission = (
        db.query(Submission)
        .filter(
            and_(
                Submission.session_id == session.id,
                Submission.student_name == submission_data.student_name,
            )
        )
        .first()
    )

    if existing_submission:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="DUPLICATE_SUBMISSION")

    # Create submission
    submission = Submission(
        session_id=session.id,
        student_name=submission_data.student_name,
        answers_json=submission_data.answers,
    )

    db.add(submission)
    db.commit()
    db.refresh(submission)

    return SubmissionOut(ok=True, submission_id=str(submission.id))


@router.get("/sessions/{session_id}/submissions", response_model=SubmissionsOut)
def get_session_submissions(session_id: str, db: Session = Depends(get_db)) -> SubmissionsOut:
    """Get all submissions for a session."""
    # Get session
    session = db.query(ClassSession).filter(ClassSession.id == session_id).first()
    if not session:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="SESSION_NOT_FOUND")

    # Get submissions
    submissions = db.query(Submission).filter(Submission.session_id == session_id).all()

    items = [
        SubmissionItem(
            student_name=str(sub.student_name),
            answers=dict(sub.answers_json) if sub.answers_json else {},
            created_at=sub.created_at,  # type: ignore[arg-type]
        )
        for sub in submissions
    ]

    return SubmissionsOut(session_id=session_id, count=len(items), items=items)
