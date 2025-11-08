from datetime import datetime
from typing import Any, List, Optional

from pydantic import BaseModel, Field


class ActivityBase(BaseModel):
    name: str
    summary: str
    type: str
    tags: List[str] = Field(default_factory=list)
    content_json: dict[str, Any]


class ActivityCreate(ActivityBase):
    pass


class ActivityPatch(BaseModel):
    name: Optional[str] = None
    summary: Optional[str] = None
    tags: Optional[List[str]] = None
    content_json: Optional[dict[str, Any]] = None


class ActivityOut(ActivityBase):
    id: str
    creator_id: Optional[str]
    creator_name: str
    creator_email: str
    created_at: datetime
    updated_at: datetime
