import uuid

from sqlalchemy import (
    JSON,
    Boolean,
    Column,
    DateTime,
    ForeignKey,
    Index,
    String,
    UniqueConstraint,
)
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from app.db import Base


class Course(Base):
    __tablename__ = "courses"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    title = Column(String(255), nullable=False)
    teacher_id = Column(String(36), ForeignKey("teachers.id", ondelete="CASCADE"), nullable=False)
    baseline_survey_id = Column(
        String(36),
        ForeignKey("surveys.id", ondelete="SET NULL"),
        nullable=True,
    )
    learning_style_categories = Column(JSON, nullable=False, default=list)
    mood_labels = Column(JSON, nullable=False, default=list)
    requires_rebaseline = Column(Boolean, nullable=False, default=False)
    created_at = Column(DateTime(timezone=True), default=func.now())
    updated_at = Column(DateTime(timezone=True), default=func.now(), onupdate=func.now())

    # Table constraints and indexes
    __table_args__ = (
        UniqueConstraint("teacher_id", "title", name="uq_course_title_per_teacher"),
        Index("ix_course_teacher_id", "teacher_id"),
    )

    # Relationships
    teacher = relationship("Teacher", back_populates="courses")
    sessions = relationship("ClassSession", back_populates="course", cascade="all, delete-orphan")
    recommendations = relationship(
        "CourseRecommendation", back_populates="course", cascade="all, delete-orphan"
    )
    student_profiles = relationship(
        "CourseStudentProfile", back_populates="course", cascade="all, delete-orphan"
    )

    def __repr__(self) -> str:
        return f"<Course id={self.id} title={self.title}>"
