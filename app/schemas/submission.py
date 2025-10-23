from datetime import datetime
from typing import Any, Dict, List

from pydantic import BaseModel


class SubmissionItem(BaseModel):
    student_name: str
    answers: Dict[str, Any]
    total_scores: Dict[
        str, int
    ]  # Dynamic category scores: {"Category1": 15, "Category2": 5, "Category3": 10}
    created_at: datetime


class SubmissionsOut(BaseModel):
    session_id: str
    count: int
    items: List[SubmissionItem]
