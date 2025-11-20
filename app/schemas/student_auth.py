from datetime import datetime
from typing import Any, Dict, List, Optional

from pydantic import BaseModel, EmailStr


class StudentSignupIn(BaseModel):
    email: EmailStr
    password: str
    full_name: str


class StudentSignupOut(BaseModel):
    id: str
    email: str
    full_name: str


class StudentLoginIn(BaseModel):
    email: EmailStr
    password: str


class StudentLoginOut(BaseModel):
    access_token: str
    token_type: str = "bearer"
    student_email: str
    student_full_name: str


class StudentProfileOut(BaseModel):
    id: str
    email: str
    full_name: str
    created_at: datetime


class StudentSubmissionHistoryItem(BaseModel):
    id: str
    session_id: str
    course_title: str
    answers: Dict[str, Any]
    total_scores: Optional[Dict[str, int]]
    status: str  # "skipped" or "completed"
    created_at: datetime
    updated_at: Optional[datetime]


class StudentSubmissionHistoryOut(BaseModel):
    submissions: List[StudentSubmissionHistoryItem]
    total: int
