import uuid

from sqlalchemy import JSON, CheckConstraint, Column, DateTime, ForeignKey, String, UniqueConstraint
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from app.db import Base


class Submission(Base):
    __tablename__ = "submissions"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    session_id = Column(String(36), ForeignKey("sessions.id", ondelete="CASCADE"), nullable=False)
    student_id = Column(
        String(36), ForeignKey("students.id", ondelete="CASCADE"), nullable=True
    )  # For authenticated students
    guest_name = Column(String(255), nullable=True)  # For guest users
    guest_id = Column(String(36), nullable=True)  # Unique guest identifier
    answers_json = Column(JSON, nullable=False)
    total_scores = Column(JSON, nullable=True)  # Store calculated scores per category
    status = Column(String(20), default="completed")  # "skipped" or "completed"
    created_at = Column(DateTime(timezone=True), default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    # Relationships
    session = relationship("ClassSession", back_populates="submissions")
    student = relationship("Student", back_populates="submissions")

    # Constraints
    __table_args__ = (
        # Exactly one of student_id or (guest_name AND guest_id) must be non-null
        CheckConstraint(
            "(student_id IS NOT NULL AND guest_name IS NULL AND guest_id IS NULL) OR "
            "(student_id IS NULL AND guest_name IS NOT NULL AND guest_id IS NOT NULL)",
            name="ck_submission_student_or_guest",
        ),
        # Unique constraints for each type
        UniqueConstraint("session_id", "student_id", name="uq_session_student"),
        UniqueConstraint("session_id", "guest_id", name="uq_session_guest_id"),
    )
