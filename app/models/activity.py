import uuid

from sqlalchemy import JSON, Column, DateTime, ForeignKey, String
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from app.db import Base


class Activity(Base):
    __tablename__ = "activities"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    name = Column(String(255), nullable=False)
    summary = Column(String(1024), nullable=False)
    type = Column(
        String(100), ForeignKey("activity_types.type_name", ondelete="RESTRICT"), nullable=False
    )
    tags = Column(JSON, nullable=False, default=list)
    content_json = Column(JSON, nullable=False, default=dict)
    creator_id = Column(String(36), ForeignKey("teachers.id", ondelete="SET NULL"), nullable=True)
    creator_name = Column(String(255), nullable=False)
    creator_email = Column(String(255), nullable=False)
    created_at = Column(DateTime(timezone=True), default=func.now())
    updated_at = Column(DateTime(timezone=True), default=func.now(), onupdate=func.now())

    # Relationships
    activity_type = relationship("ActivityType", back_populates="activities")
    creator = relationship("Teacher", back_populates="activities")
    recommendations = relationship(
        "CourseRecommendation", back_populates="activity", cascade="all, delete-orphan"
    )

    def __repr__(self) -> str:
        return f"<Activity id={self.id} name={self.name}>"
