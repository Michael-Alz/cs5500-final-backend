from typing import Dict, List, Optional

from pydantic import BaseModel

from app.schemas.recommendations import RecommendedActivityOut


class PublicSurveyOption(BaseModel):
    option_id: str
    text: str


class PublicSurveyQuestion(BaseModel):
    question_id: str
    text: str
    options: List[PublicSurveyOption]


class PublicSurveySnapshot(BaseModel):
    survey_id: str
    title: str
    questions: List[PublicSurveyQuestion]


class MoodCheckSchema(BaseModel):
    prompt: str
    options: List[str]


class PublicJoinOut(BaseModel):
    session_id: str
    course_id: str
    course_title: str
    require_survey: bool
    mood_check_schema: MoodCheckSchema
    survey: Optional[PublicSurveySnapshot]
    status: str


class SubmissionIn(BaseModel):
    mood: str
    answers: Optional[Dict[str, str]] = None
    is_guest: bool = True
    student_name: Optional[str] = None
    guest_id: Optional[str] = None


class SubmissionOut(BaseModel):
    submission_id: str
    student_id: Optional[str] = None
    guest_id: Optional[str] = None
    require_survey: bool
    is_baseline_update: bool
    mood: str
    learning_style: Optional[str] = None
    total_scores: Optional[Dict[str, int]] = None
    recommended_activity: RecommendedActivityOut
    message: str


class SubmissionStatusOut(BaseModel):
    submitted: bool
