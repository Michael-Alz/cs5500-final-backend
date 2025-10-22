from typing import Any, Dict, List

from pydantic import BaseModel


class PublicJoinOut(BaseModel):
    session_id: str
    course_title: str
    survey_schema: List[dict[str, Any]]
    status: str


class SubmissionIn(BaseModel):
    student_name: str
    answers: Dict[str, Any]


class SubmissionOut(BaseModel):
    ok: bool
    submission_id: str
