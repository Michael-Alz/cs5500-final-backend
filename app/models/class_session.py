import uuid

from sqlalchemy import JSON, Boolean, Column, DateTime, ForeignKey, String
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from app.db import Base


class ClassSession(Base):
    __tablename__ = "sessions"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    course_id = Column(String(36), ForeignKey("courses.id", ondelete="CASCADE"), nullable=False)
    survey_template_id = Column(
        String(36), ForeignKey("surveys.id", ondelete="RESTRICT"), nullable=True
    )
    require_survey = Column(Boolean, nullable=False, default=False)
    mood_check_schema = Column(JSON, nullable=False, default=dict)
    survey_snapshot_json = Column(JSON, nullable=True)
    started_at = Column(DateTime(timezone=True), default=func.now())
    closed_at = Column(DateTime(timezone=True), nullable=True)
    join_token = Column(String(16), unique=True, nullable=False, index=True)

    # Relationships
    course = relationship("Course", back_populates="sessions")
    survey_template = relationship("SurveyTemplate", back_populates="sessions")
    submissions = relationship("Submission", back_populates="session", cascade="all, delete-orphan")

    def __repr__(self) -> str:
        return f"<Session id={self.id} course={self.course_id}>"
