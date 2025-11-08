import uuid

from sqlalchemy import Boolean, Column, DateTime, ForeignKey, Index, String, UniqueConstraint
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from app.db import Base


class CourseRecommendation(Base):
    __tablename__ = "course_recommendations"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    course_id = Column(String(36), ForeignKey("courses.id", ondelete="CASCADE"), nullable=False)
    learning_style = Column(String(100), nullable=True)
    mood = Column(String(100), nullable=True)
    activity_id = Column(
        String(36), ForeignKey("activities.id", ondelete="CASCADE"), nullable=False
    )
    is_auto = Column(Boolean, nullable=False, default=False, server_default="false")
    created_at = Column(DateTime(timezone=True), default=func.now())
    updated_at = Column(DateTime(timezone=True), default=func.now(), onupdate=func.now())

    # Table constraints
    __table_args__ = (
        UniqueConstraint(
            "course_id",
            "learning_style",
            "mood",
            name="uq_course_style_mood",
        ),
        Index("ix_course_recommendations_course", "course_id"),
    )

    # Relationships
    course = relationship("Course", back_populates="recommendations")
    activity = relationship("Activity", back_populates="recommendations")

    def __repr__(self) -> str:
        return (
            f"<CourseRecommendation course={self.course_id} "
            f"style={self.learning_style} mood={self.mood}>"
        )
