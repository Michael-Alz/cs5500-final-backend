import uuid

from sqlalchemy import JSON, Column, DateTime, Index, String
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from app.db import Base


class SurveyTemplate(Base):  # type: ignore[misc]
    __tablename__ = "survey_templates"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    title = Column(String(255), nullable=False, unique=True, index=True)
    questions_json = Column(JSON, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    # Relationships
    sessions = relationship("ClassSession", back_populates="survey_template")

    # Table constraints and indexes
    __table_args__ = (Index("ix_survey_template_title", "title", unique=True),)

    def __repr__(self) -> str:
        return f"<SurveyTemplate id={self.id} title={self.title}>"
