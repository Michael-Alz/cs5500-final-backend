from typing import Any, Dict, List, Optional

from pydantic import BaseModel


class PublicJoinOut(BaseModel):
    session_id: str
    course_title: str
    survey_schema: List[Dict[str, Any]]
    status: str


class SubmissionIn(BaseModel):
    student_name: Optional[str] = None  # For guest users
    guest_id: Optional[str] = None  # For guest users (for retaking)
    answers: Dict[str, Any]
    is_guest: bool = True  # Default to guest mode


class SubmissionOut(BaseModel):
    ok: bool
    submission_id: str
    guest_id: Optional[str] = None  # For guest submissions
    status: str  # "skipped" or "completed"
