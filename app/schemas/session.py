from datetime import datetime
from typing import Any, Dict, List, Literal, Optional

from pydantic import BaseModel

from app.schemas.recommendations import RecommendedActivityOut


class MoodCheckSchema(BaseModel):
    prompt: str
    options: List[str]


class SessionCreate(BaseModel):
    require_survey: Optional[bool] = False


class SessionOut(BaseModel):
    session_id: str
    course_id: str
    require_survey: bool
    mood_check_schema: MoodCheckSchema
    survey_snapshot_json: Optional[Dict[str, Any]]
    started_at: datetime
    closed_at: Optional[datetime]
    join_token: str
    qr_url: str

    class Config:
        from_attributes = True


class SessionCloseOut(BaseModel):
    status: str


class SessionDashboardParticipant(BaseModel):
    display_name: str
    mode: Literal["student", "guest"]
    student_id: Optional[str] = None
    guest_id: Optional[str] = None
    mood: str
    learning_style: Optional[str] = None
    recommended_activity: RecommendedActivityOut


class SessionDashboardOut(BaseModel):
    session_id: str
    course_id: str
    course_title: str
    require_survey: bool
    mood_summary: Dict[str, int]
    participants: List[SessionDashboardParticipant]
