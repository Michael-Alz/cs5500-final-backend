from typing import Any, Optional

from pydantic import BaseModel


class RecommendationActivityDetails(BaseModel):
    activity_id: str
    name: str
    summary: str
    type: str
    content_json: dict[str, Any]


class RecommendedActivityOut(BaseModel):
    match_type: str
    learning_style: Optional[str]
    mood: str
    activity: Optional[RecommendationActivityDetails]
