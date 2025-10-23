from typing import List

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.api.deps import get_current_teacher
from app.db import get_db
from app.models.survey_template import SurveyTemplate
from app.models.teacher import Teacher
from app.schemas.survey_template import SurveyTemplateCreate, SurveyTemplateOut

router = APIRouter()


def validate_survey_questions(questions: List[dict]) -> None:
    """Validate survey questions structure according to requirements.

    This function validates that all questions have consistent category structure
    and that each option has exactly one positive score across all categories.
    """
    if len(questions) != 8:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="VALIDATION_ERROR: Must have exactly 8 questions",
        )

    # Dynamically extract all categories from the survey
    all_categories = set()
    for question in questions:
        for option in question.get("options", []):
            scores = option.get("scores", {})
            all_categories.update(scores.keys())

    if not all_categories:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="VALIDATION_ERROR: No categories found in survey options",
        )

    for i, question in enumerate(questions):
        # Check required fields
        if not isinstance(question, dict):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"VALIDATION_ERROR: Question {i + 1} must be an object",
            )

        if "id" not in question or not isinstance(question["id"], str):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"VALIDATION_ERROR: Question {i + 1} must have a string 'id' field",
            )

        if "text" not in question or not isinstance(question["text"], str):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"VALIDATION_ERROR: Question {i + 1} must have a string 'text' field",
            )

        if "options" not in question or not isinstance(question["options"], list):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"VALIDATION_ERROR: Question {i + 1} must have an 'options' array",
            )

        if len(question["options"]) != 3:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"VALIDATION_ERROR: Question {i + 1} must have exactly 3 options",
            )

        # Validate each option
        for j, option in enumerate(question["options"]):
            if not isinstance(option, dict):
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"VALIDATION_ERROR: Question {i + 1}, option {j + 1} must be an object",
                )

            if "label" not in option or not isinstance(option["label"], str):
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=(
                        f"VALIDATION_ERROR: Question {i + 1}, option {j + 1} "
                        f"must have a string 'label' field"
                    ),
                )

            if "scores" not in option or not isinstance(option["scores"], dict):
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=(
                        f"VALIDATION_ERROR: Question {i + 1}, option {j + 1} "
                        f"must have a 'scores' object"
                    ),
                )

            scores = option["scores"]
            positive_scores = 0
            total_score = 0

            # Validate that all categories are present and have valid scores
            for category in all_categories:
                if category not in scores:
                    raise HTTPException(
                        status_code=status.HTTP_400_BAD_REQUEST,
                        detail=(
                            f"VALIDATION_ERROR: Question {i + 1}, option {j + 1} "
                            f"missing category '{category}' in scores"
                        ),
                    )

                if not isinstance(scores[category], (int, float)):
                    raise HTTPException(
                        status_code=status.HTTP_400_BAD_REQUEST,
                        detail=(
                            f"VALIDATION_ERROR: Question {i + 1}, option {j + 1} "
                            f"score for '{category}' must be a number"
                        ),
                    )

                if scores[category] > 0:
                    positive_scores += 1
                total_score += scores[category]

            if positive_scores != 1:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=(
                        f"VALIDATION_ERROR: Question {i + 1}, option {j + 1} "
                        f"must have exactly one positive score"
                    ),
                )


@router.post("/", response_model=SurveyTemplateOut)
def create_survey(
    survey_data: SurveyTemplateCreate,
    db: Session = Depends(get_db),
    current_teacher: Teacher = Depends(get_current_teacher),
) -> SurveyTemplateOut:
    """
    Create a new survey template.
    Auth required. Template will be globally visible to all teachers.
    """
    # Validate questions structure
    validate_survey_questions(survey_data.questions)

    # Check if title already exists
    existing_template = (
        db.query(SurveyTemplate).filter(SurveyTemplate.title == survey_data.title).first()
    )
    if existing_template:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="DUPLICATE_TITLE")

    # Create new survey template
    template = SurveyTemplate(
        title=survey_data.title,
        questions_json=survey_data.questions,
        creator_name=current_teacher.email,  # Use email as creator name
    )

    db.add(template)
    db.commit()
    db.refresh(template)

    return SurveyTemplateOut(
        id=str(template.id),
        title=str(template.title),
        questions=template.questions_json or [],  # type: ignore[arg-type]
        creator_name=str(template.creator_name),
        created_at=template.created_at,  # type: ignore[arg-type]
    )


@router.get("/", response_model=List[SurveyTemplateOut])
def list_surveys(
    db: Session = Depends(get_db), current_teacher: Teacher = Depends(get_current_teacher)
) -> List[SurveyTemplateOut]:
    """
    List all available survey templates.
    Auth required but all teachers see the same library (no owner filter).
    """
    templates = db.query(SurveyTemplate).order_by(SurveyTemplate.created_at.asc()).all()
    return [
        SurveyTemplateOut(
            id=str(t.id),
            title=str(t.title),
            questions=t.questions_json or [],  # type: ignore[arg-type]
            creator_name=str(t.creator_name),
            created_at=t.created_at,  # type: ignore[arg-type]
        )
        for t in templates
    ]
