from typing import Any, List

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.api.deps import get_current_teacher
from app.db import get_db
from app.models.survey_template import SurveyTemplate
from app.models.teacher import Teacher
from app.schemas.survey_template import SurveyTemplateIn, SurveyTemplateOut

router = APIRouter()


def validate_survey_questions(questions: List[dict[str, Any]]) -> None:
    """Validate survey questions structure."""
    if not questions:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="Survey must have at least one question"
        )

    for i, question in enumerate(questions):
        if not isinstance(question, dict):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Question {i+1} must be a dictionary",
            )

        if "id" not in question:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Question {i+1} must have an 'id' field",
            )

        if "text" not in question:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Question {i+1} must have a 'text' field",
            )

        if "options" not in question:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Question {i+1} must have an 'options' field",
            )

        options = question.get("options", [])
        if not isinstance(options, list) or len(options) == 0:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Question {i+1} must have at least one option",
            )

        # Validate each option
        for j, option in enumerate(options):
            if not isinstance(option, dict):
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"Question {i+1}, Option {j+1} must be a dictionary",
                )

            if "label" not in option:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"Question {i+1}, Option {j+1} must have a 'label' field",
                )

            if "scores" not in option:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"Question {i+1}, Option {j+1} must have a 'scores' field",
                )

            scores = option.get("scores", {})
            if not isinstance(scores, dict):
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"Question {i+1}, Option {j+1} scores must be a dictionary",
                )

            # Validate that scores are numeric
            for category, score in scores.items():
                if not isinstance(score, (int, float)):
                    raise HTTPException(
                        status_code=status.HTTP_400_BAD_REQUEST,
                        detail=(
                            f"Question {i+1}, Option {j+1}, Category '{category}' "
                            f"score must be numeric"
                        ),
                    )


@router.post("/", response_model=SurveyTemplateOut)
def create_survey(
    survey_data: SurveyTemplateIn,
    db: Session = Depends(get_db),
    current_teacher: Teacher = Depends(get_current_teacher),
) -> SurveyTemplateOut:
    """Create a new survey template."""
    # Validate questions structure
    validate_survey_questions(survey_data.questions)

    # Check if survey with same title already exists
    existing_survey = (
        db.query(SurveyTemplate).filter(SurveyTemplate.title == survey_data.title).first()
    )

    if existing_survey:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="Survey with this title already exists"
        )

    # Create new survey template
    template = SurveyTemplate(
        title=survey_data.title,
        questions_json=survey_data.questions,
        creator_name=current_teacher.full_name or "Unknown Teacher",
        creator_id=current_teacher.id,
        creator_email=current_teacher.email,
    )

    db.add(template)
    db.commit()
    db.refresh(template)

    # Return the created survey
    questions_data: list[dict[str, Any]] = template.questions_json or []  # type: ignore[assignment]
    assert isinstance(questions_data, list)
    return SurveyTemplateOut(
        id=str(template.id),
        title=str(template.title),
        questions=questions_data,
        creator_name=str(template.creator_name),
        creator_id=str(template.creator_id) if template.creator_id else None,
        creator_email=str(template.creator_email) if template.creator_email else None,
        created_at=template.created_at,  # type: ignore[arg-type]
        total=len(questions_data),
    )


@router.get("/", response_model=List[SurveyTemplateOut])
def list_surveys(
    db: Session = Depends(get_db),
    current_teacher: Teacher = Depends(get_current_teacher),
) -> List[SurveyTemplateOut]:
    """List all available survey templates."""
    templates = db.query(SurveyTemplate).order_by(SurveyTemplate.created_at.desc()).all()

    result = []
    for t in templates:
        questions_data: list[dict[str, Any]] = t.questions_json or []  # type: ignore[assignment]
        assert isinstance(questions_data, list)
        result.append(
            SurveyTemplateOut(
                id=str(t.id),
                title=str(t.title),
                questions=questions_data,
                creator_name=str(t.creator_name),
                creator_id=str(t.creator_id) if t.creator_id else None,
                creator_email=str(t.creator_email) if t.creator_email else None,
                created_at=t.created_at,  # type: ignore[arg-type]
                total=len(questions_data),
            )
        )

    return result


@router.get("/{survey_id}", response_model=SurveyTemplateOut)
def get_survey(
    survey_id: str,
    db: Session = Depends(get_db),
    current_teacher: Teacher = Depends(get_current_teacher),
) -> SurveyTemplateOut:
    """Get a specific survey template by ID."""
    template = db.query(SurveyTemplate).filter(SurveyTemplate.id == survey_id).first()

    if not template:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Survey template not found"
        )

    questions_data: list[dict[str, Any]] = template.questions_json or []  # type: ignore[assignment]
    assert isinstance(questions_data, list)
    return SurveyTemplateOut(
        id=str(template.id),
        title=str(template.title),
        questions=questions_data,
        creator_name=str(template.creator_name),
        creator_id=str(template.creator_id) if template.creator_id else None,
        creator_email=str(template.creator_email) if template.creator_email else None,
        created_at=template.created_at,  # type: ignore[arg-type]
        total=len(questions_data),
    )
