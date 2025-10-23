import uuid

from sqlalchemy import JSON, Column, DateTime, ForeignKey, String, UniqueConstraint
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from app.db import Base


class Submission(Base):
    __tablename__ = "submissions"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    session_id = Column(String(36), ForeignKey("sessions.id", ondelete="CASCADE"), nullable=False)
    student_name = Column(String(255), nullable=False)
    answers_json = Column(JSON, nullable=False)
    total_scores = Column(JSON, nullable=True)  # Store calculated scores per category
    created_at = Column(DateTime(timezone=True), default=func.now())

    # Relationships
    session = relationship("ClassSession", back_populates="submissions")

    # Unique constraint to prevent duplicate submissions
    __table_args__ = (UniqueConstraint("session_id", "student_name", name="uq_session_student"),)
