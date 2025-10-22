from typing import List

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.api.deps import get_current_teacher
from app.db import get_db
from app.models.survey_template import SurveyTemplate
from app.models.teacher import Teacher
from app.schemas.survey_template import SurveyTemplateOut

router = APIRouter()


@router.get("/", response_model=List[SurveyTemplateOut])
def list_survey_templates(
    db: Session = Depends(get_db), current_teacher: Teacher = Depends(get_current_teacher)
) -> List[SurveyTemplateOut]:
    """
    List all available survey templates.
    Auth required but all teachers see the same library (no owner filter).
    """
    templates = db.query(SurveyTemplate).order_by(SurveyTemplate.created_at.asc()).all()
    return [
        SurveyTemplateOut(id=str(t.id), title=str(t.title), questions=t.questions_json or [])  # type: ignore[arg-type]
        for t in templates
    ]
