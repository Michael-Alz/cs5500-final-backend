import uuid

from sqlalchemy import JSON, Boolean, Column, DateTime, ForeignKey, String, UniqueConstraint
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from app.db import Base


class CourseStudentProfile(Base):
    __tablename__ = "course_student_profiles"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    course_id = Column(String(36), ForeignKey("courses.id", ondelete="CASCADE"), nullable=False)
    student_id = Column(String(36), ForeignKey("students.id", ondelete="CASCADE"), nullable=True)
    guest_id = Column(String(36), nullable=True)
    latest_submission_id = Column(
        String(36), ForeignKey("submissions.id", ondelete="SET NULL"), nullable=True
    )
    profile_category = Column(String(100), nullable=False)
    profile_scores_json = Column(JSON, nullable=False, default=dict)
    first_captured_at = Column(DateTime(timezone=True), default=func.now())
    updated_at = Column(DateTime(timezone=True), default=func.now(), onupdate=func.now())
    is_current = Column(Boolean, nullable=False, default=True)

    __table_args__ = (
        UniqueConstraint(
            "course_id",
            "student_id",
            "is_current",
            name="uq_course_student_current",
        ),
        UniqueConstraint(
            "course_id",
            "guest_id",
            "is_current",
            name="uq_course_guest_current",
        ),
    )

    # Relationships
    course = relationship("Course", back_populates="student_profiles")
    student = relationship("Student", back_populates="course_profiles")
    latest_submission = relationship("Submission")

    def __repr__(self) -> str:
        participant = self.student_id or self.guest_id
        return (
            f"<CourseStudentProfile course={self.course_id} participant={participant} "
            f"category={self.profile_category} current={self.is_current}>"
        )
