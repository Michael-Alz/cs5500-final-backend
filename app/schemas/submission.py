from datetime import datetime
from typing import Any, Dict, List, Optional

from pydantic import BaseModel


class SubmissionItem(BaseModel):
    student_name: Optional[str] = None  # For guest users
    student_id: Optional[str] = None  # For authenticated students
    student_full_name: Optional[str] = None  # For authenticated students
    mood: str
    answers: Optional[Dict[str, Any]] = None
    answer_details: Optional[Dict[str, Any]] = None
    total_scores: Optional[Dict[str, int]] = None  # Dynamic category scores
    learning_style: Optional[str] = None
    is_baseline_update: bool
    status: str  # "skipped" or "completed"
    created_at: datetime
    updated_at: Optional[datetime] = None


class SubmissionsOut(BaseModel):
    session_id: str
    count: int
    items: List[SubmissionItem]
