from datetime import datetime
from typing import Any, Dict, List

from pydantic import BaseModel


class SurveyTemplateCreate(BaseModel):
    title: str
    questions: List[
        Dict[str, Any]
    ]  # will be validated as the same shape used by existing templates


class SurveyTemplateOut(BaseModel):
    id: str
    title: str
    questions: List[Dict[str, Any]]  # exactly the JSON stored in questions_json
    creator_name: str
    created_at: datetime

    class Config:
        from_attributes = True


class SurveyTemplateListItem(BaseModel):
    id: str
    title: str
    question_count: int

    class Config:
        from_attributes = True
