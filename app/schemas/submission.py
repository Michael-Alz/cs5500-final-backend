from datetime import datetime
from typing import Any, Dict, List

from pydantic import BaseModel


class SubmissionItem(BaseModel):
    student_name: str
    answers: Dict[str, Any]
    created_at: datetime


class SubmissionsOut(BaseModel):
    session_id: str
    count: int
    items: List[SubmissionItem]
