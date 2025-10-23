from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import and_
from sqlalchemy.orm import Session

from app.db import get_db
from app.models.class_session import ClassSession
from app.models.submission import Submission
from app.models.survey_template import SurveyTemplate
from app.schemas.public import PublicJoinOut, SubmissionIn, SubmissionOut

router = APIRouter()


def calculate_survey_scores(session: ClassSession, student_answers: dict, db: Session) -> dict:
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
    for question in survey_template.questions_json:
        for option in question.get("options", []):
            scores = option.get("scores", {})
            all_categories.update(scores.keys())

    # Initialize score totals dynamically
    total_scores = {category: 0 for category in all_categories}

    # Process each question
    for question in survey_template.questions_json:
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

    # Calculate scores for the submission
    total_scores = calculate_survey_scores(session, submission_data.answers, db)

    # Create submission with calculated scores
    submission = Submission(
        session_id=session.id,
        student_name=submission_data.student_name,
        answers_json=submission_data.answers,
        total_scores=total_scores,
    )

    db.add(submission)
    db.commit()
    db.refresh(submission)

    return SubmissionOut(ok=True, submission_id=str(submission.id))
