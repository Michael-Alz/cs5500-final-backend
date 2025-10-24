from datetime import datetime
from typing import Any, List

from pydantic import BaseModel


class SurveyTemplateIn(BaseModel):
    title: str
    questions: List[dict[str, Any]]


class SurveyTemplateOut(BaseModel):
    id: str
    title: str
    questions: List[dict[str, Any]]
    creator_name: str
    creator_id: str | None = None
    creator_email: str | None = None
    created_at: datetime

    total: int
