from sqlalchemy import JSON, Column, DateTime, String
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from app.db import Base


class ActivityType(Base):
    __tablename__ = "activity_types"

    type_name = Column(String(100), primary_key=True)
    description = Column(String(1024), nullable=False)
    required_fields = Column(JSON, nullable=False, default=list)
    optional_fields = Column(JSON, nullable=False, default=list)
    example_content_json = Column(JSON, nullable=True)
    created_at = Column(DateTime(timezone=True), default=func.now())
    updated_at = Column(DateTime(timezone=True), default=func.now(), onupdate=func.now())

    # Relationships
    activities = relationship("Activity", back_populates="activity_type")

    def __repr__(self) -> str:
        return f"<ActivityType type_name={self.type_name}>"
