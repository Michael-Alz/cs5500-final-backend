from typing import List

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.api.deps import get_current_teacher
from app.db import get_db
from app.models.activity_type import ActivityType
from app.models.teacher import Teacher
from app.schemas.activity_type import ActivityTypeCreate, ActivityTypeOut

router = APIRouter()


def _to_schema(activity_type: ActivityType) -> ActivityTypeOut:
    return ActivityTypeOut.model_validate(activity_type, from_attributes=True)


@router.get("/", response_model=List[ActivityTypeOut])
def list_activity_types(db: Session = Depends(get_db)) -> List[ActivityTypeOut]:
    types = db.query(ActivityType).order_by(ActivityType.type_name.asc()).all()
    return [_to_schema(activity_type) for activity_type in types]


@router.post("/", response_model=ActivityTypeOut, status_code=status.HTTP_201_CREATED)
def create_activity_type(
    payload: ActivityTypeCreate,
    db: Session = Depends(get_db),
    _current_teacher: Teacher = Depends(get_current_teacher),
) -> ActivityTypeOut:
    existing = db.query(ActivityType).filter(ActivityType.type_name == payload.type_name).first()
    if existing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="ACTIVITY_TYPE_EXISTS",
        )

    activity_type = ActivityType(
        type_name=payload.type_name,
        description=payload.description,
        required_fields=list(payload.required_fields),
        optional_fields=list(payload.optional_fields),
        example_content_json=dict(payload.example_content_json or {}),
    )

    db.add(activity_type)
    db.commit()
    db.refresh(activity_type)
    return _to_schema(activity_type)
