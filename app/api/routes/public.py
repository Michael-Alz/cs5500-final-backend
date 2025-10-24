import uuid
from typing import Any, Optional

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import and_
from sqlalchemy.orm import Session

from app.api.deps import get_current_student_optional
from app.db import get_db
from app.models.class_session import ClassSession
from app.models.student import Student
from app.models.submission import Submission
from app.models.survey_template import SurveyTemplate
from app.schemas.public import PublicJoinOut, SubmissionIn, SubmissionOut

router = APIRouter()


def calculate_survey_scores(
    session: ClassSession,
    student_answers: dict[str, str],
    db: Session,
) -> dict[str, int]:
    """Calculate total scores for each category based on student answers.

    This function dynamically detects all categories from the survey template
    and calculates scores accordingly, supporting any number of categories.
    """
    # Get the survey template for this session
    survey_template = (
        db.query(SurveyTemplate).filter(SurveyTemplate.id == session.survey_template_id).first()
    )

    if not survey_template or not survey_template.questions_json:
        return {}

    # Dynamically extract all categories from the survey template
    all_categories = set()
    questions_data: list[dict[str, Any]] = survey_template.questions_json or []  # type: ignore[assignment]
    assert isinstance(questions_data, list)
    for question in questions_data:
        for option in question.get("options", []):
            scores = option.get("scores", {})
            all_categories.update(scores.keys())

    # Initialize score totals dynamically
    total_scores = {category: 0 for category in all_categories}

    # Process each question
    for question in questions_data:
        question_id = question.get("id")
        if question_id not in student_answers:
            continue

        selected_answer = student_answers[question_id]

        # Find the matching option and its scores
        for option in question.get("options", []):
            if option.get("label") == selected_answer:
                scores = option.get("scores", {})
                for category, score in scores.items():
                    if category in total_scores:
                        total_scores[category] += score
                break

    return total_scores


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
    join_token: str,
    submission_data: SubmissionIn,
    db: Session = Depends(get_db),
    current_student: Optional[Student] = Depends(get_current_student_optional),
) -> SubmissionOut:
    """Submit a survey response."""

    # Find session by token
    session = db.query(ClassSession).filter(ClassSession.join_token == join_token).first()

    if not session:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="SESSION_NOT_FOUND")

    if session.closed_at is not None:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="SESSION_CLOSED")

    # Determine if this is a guest or student submission
    is_guest = submission_data.is_guest or not current_student

    # Validate submission data based on mode
    if is_guest:
        if not submission_data.student_name or not submission_data.student_name.strip():
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST, detail="GUEST_NAME_REQUIRED"
            )
    else:
        # For authenticated students, ignore the student_name field
        pass

    # Determine submission status
    submission_status = "skipped" if not submission_data.answers else "completed"

    # Calculate scores only if not skipped
    total_scores = {}
    if submission_status == "completed":
        total_scores = calculate_survey_scores(session, submission_data.answers, db)

    # Check for existing submission
    existing_submission = None
    guest_id = None

    if is_guest:
        # For guest submissions, we need to check if there's a guest_id in the request
        # If not, we'll generate a new one for new submissions
        guest_id = getattr(submission_data, "guest_id", None)

        if guest_id:
            # Look for existing submission by guest_id
            existing_submission = (
                db.query(Submission)
                .filter(
                    and_(
                        Submission.session_id == session.id,
                        Submission.guest_id == guest_id,
                    )
                )
                .first()
            )
        else:
            # For new guest submissions, generate a guest_id
            guest_id = str(uuid.uuid4())
    else:
        existing_submission = (
            db.query(Submission)
            .filter(
                and_(
                    Submission.session_id == session.id,
                    Submission.student_id == current_student.id,
                )
            )
            .first()
        )

    if existing_submission:
        # Update existing submission
        existing_submission.answers_json = submission_data.answers
        existing_submission.total_scores = total_scores
        existing_submission.status = submission_status
        db.commit()
        db.refresh(existing_submission)

        return SubmissionOut(
            ok=True,
            submission_id=str(existing_submission.id),
            guest_id=(
                str(existing_submission.guest_id)
                if is_guest and existing_submission.guest_id
                else None
            ),
            status=submission_status,
        )
    else:
        # Create new submission
        submission = Submission(
            session_id=session.id,
            student_id=current_student.id if not is_guest and current_student else None,
            guest_name=submission_data.student_name if is_guest else None,
            guest_id=guest_id if is_guest else None,
            answers_json=submission_data.answers,
            total_scores=total_scores,
            status=submission_status,
        )

        db.add(submission)
        db.commit()
        db.refresh(submission)

        return SubmissionOut(
            ok=True,
            submission_id=str(submission.id),
            guest_id=str(submission.guest_id) if is_guest and submission.guest_id else None,
            status=submission_status,
        )


@router.get("/join/{join_token}/submission")
def get_submission_status(
    join_token: str,
    guest_id: Optional[str] = None,
    db: Session = Depends(get_db),
    current_student: Optional[Student] = Depends(get_current_student_optional),
) -> dict[str, Any]:
    """Get submission status for a session (for checking if already submitted)."""
    # Find session by token
    session = db.query(ClassSession).filter(ClassSession.join_token == join_token).first()

    if not session:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="SESSION_NOT_FOUND")

    # Determine if this is a guest or student request
    is_guest = not current_student

    if is_guest:
        if not guest_id:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="GUEST_ID_REQUIRED")

        submission = (
            db.query(Submission)
            .filter(
                and_(
                    Submission.session_id == session.id,
                    Submission.guest_id == guest_id,
                )
            )
            .first()
        )
    else:
        if not current_student:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="STUDENT_REQUIRED")
        submission = (
            db.query(Submission)
            .filter(
                and_(
                    Submission.session_id == session.id,
                    Submission.student_id == current_student.id,
                )
            )
            .first()
        )

    if not submission:
        return {"submitted": False}

    return {
        "submitted": True,
        "submission_id": str(submission.id),
        "status": str(submission.status),
        "created_at": submission.created_at,
        "updated_at": submission.updated_at,
    }
