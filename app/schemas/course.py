from datetime import datetime
from typing import Any, List, Optional

from pydantic import BaseModel, Field


class CourseCreate(BaseModel):
    title: str
    baseline_survey_id: str
    mood_labels: List[str] = Field(min_length=1)


class CourseUpdate(BaseModel):
    title: Optional[str] = None
    baseline_survey_id: Optional[str] = None


class CourseOut(BaseModel):
    id: str
    title: str
    baseline_survey_id: Optional[str] = None
    learning_style_categories: List[str]
    mood_labels: List[str]
    requires_rebaseline: bool
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True


class CourseRecommendationMapping(BaseModel):
    learning_style: Optional[str] = None
    mood: Optional[str] = None
    activity_id: str


class CourseRecommendationActivity(BaseModel):
    activity_id: str
    name: str
    summary: str
    type: str
    content_json: dict[str, Any]


class CourseRecommendationOutItem(BaseModel):
    learning_style: Optional[str]
    mood: Optional[str]
    activity: Optional[CourseRecommendationActivity]


class CourseRecommendationsOut(BaseModel):
    course_id: str
    learning_style_categories: List[str]
    mood_labels: List[str]
    mappings: List[CourseRecommendationOutItem]


class CourseRecommendationsPatchIn(BaseModel):
    mappings: List[CourseRecommendationMapping]
