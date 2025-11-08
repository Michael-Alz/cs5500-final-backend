from datetime import datetime
from typing import Any, List, Optional

from pydantic import BaseModel


class ActivityTypeBase(BaseModel):
    type_name: str
    description: str
    required_fields: List[str]
    optional_fields: List[str]
    example_content_json: Optional[dict[str, Any]] = None


class ActivityTypeCreate(ActivityTypeBase):
    pass


class ActivityTypeOut(ActivityTypeBase):
    created_at: datetime
    updated_at: datetime
