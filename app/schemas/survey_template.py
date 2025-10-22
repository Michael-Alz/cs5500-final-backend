from typing import Any, Dict, List

from pydantic import BaseModel


class SurveyTemplateOut(BaseModel):
    id: str
    title: str
    questions: List[Dict[str, Any]]  # exactly the JSON stored in questions_json

    class Config:
        from_attributes = True


class SurveyTemplateListItem(BaseModel):
    id: str
    title: str
    question_count: int

    class Config:
        from_attributes = True
