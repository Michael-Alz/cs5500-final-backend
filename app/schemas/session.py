from datetime import datetime
from typing import Any, List, Optional

from pydantic import BaseModel


class SessionCreate(BaseModel):
    survey_template_id: str


class SessionOut(BaseModel):
    session_id: str
    course_id: str
    started_at: datetime
    closed_at: Optional[datetime]
    join_token: str
    qr_url: str
    survey_schema: List[dict[str, Any]]

    class Config:
        from_attributes = True


class SessionCloseOut(BaseModel):
    status: str
