import uuid

from sqlalchemy import Column, DateTime, ForeignKey, Index, String, UniqueConstraint
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from app.db import Base


class Course(Base):  # type: ignore[misc]
    __tablename__ = "courses"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    title = Column(String(255), nullable=False)
    teacher_id = Column(String(36), ForeignKey("teachers.id", ondelete="CASCADE"), nullable=False)
    created_at = Column(DateTime(timezone=True), default=func.now())

    # Table constraints and indexes
    __table_args__ = (
        UniqueConstraint("teacher_id", "title", name="uq_course_title_per_teacher"),
        Index("ix_course_teacher_id", "teacher_id"),
    )

    # Relationships
    teacher = relationship("Teacher", back_populates="courses")
    sessions = relationship("ClassSession", back_populates="course", cascade="all, delete-orphan")

    def __repr__(self) -> str:
        return f"<Course id={self.id} title={self.title}>"
