from typing import List, Optional

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from app.api.deps import get_current_teacher
from app.db import get_db
from app.models.activity import Activity
from app.models.activity_type import ActivityType
from app.models.teacher import Teacher
from app.schemas.activity import ActivityCreate, ActivityOut, ActivityPatch

router = APIRouter()


def _validate_activity_content(activity_type: ActivityType, content_json: dict) -> None:
    missing = [field for field in activity_type.required_fields if field not in content_json]
    if missing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={"code": "MISSING_REQUIRED_FIELDS", "fields": missing},
        )


def _activity_to_schema(activity: Activity) -> ActivityOut:
    return ActivityOut.model_validate(activity, from_attributes=True)


@router.get("/", response_model=List[ActivityOut])
def list_activities(
    tag: Optional[str] = Query(default=None),
    type_filter: Optional[str] = Query(default=None, alias="type"),
    db: Session = Depends(get_db),
) -> List[ActivityOut]:
    """List activities with optional filters for tag and type."""
    query = db.query(Activity)

    if type_filter:
        query = query.filter(Activity.type == type_filter)
    if tag:
        query = query.filter(Activity.tags.contains([tag]))

    activities = query.order_by(Activity.created_at.desc()).all()
    return [_activity_to_schema(activity) for activity in activities]


@router.get("/{activity_id}", response_model=ActivityOut)
def get_activity(activity_id: str, db: Session = Depends(get_db)) -> ActivityOut:
    """Retrieve a single activity by ID."""
    activity = db.query(Activity).filter(Activity.id == activity_id).first()
    if not activity:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="ACTIVITY_NOT_FOUND")
    return _activity_to_schema(activity)


@router.post("/", response_model=ActivityOut, status_code=status.HTTP_201_CREATED)
def create_activity(
    payload: ActivityCreate,
    db: Session = Depends(get_db),
    current_teacher: Teacher = Depends(get_current_teacher),
) -> ActivityOut:
    """Create a new activity."""
    activity_type = db.query(ActivityType).filter(ActivityType.type_name == payload.type).first()
    if not activity_type:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="ACTIVITY_TYPE_NOT_FOUND",
        )

    if not isinstance(payload.content_json, dict):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="CONTENT_JSON_MUST_BE_OBJECT",
        )

    _validate_activity_content(activity_type, payload.content_json)

    activity = Activity(
        name=payload.name,
        summary=payload.summary,
        type=payload.type,
        tags=list(payload.tags),
        content_json=dict(payload.content_json),
        creator_id=current_teacher.id,
        creator_name=current_teacher.full_name or current_teacher.email,
        creator_email=current_teacher.email,
    )

    db.add(activity)
    db.commit()
    db.refresh(activity)
    return _activity_to_schema(activity)


@router.patch("/{activity_id}", response_model=ActivityOut)
def update_activity(
    activity_id: str,
    payload: ActivityPatch,
    db: Session = Depends(get_db),
    current_teacher: Teacher = Depends(get_current_teacher),
) -> ActivityOut:
    """Update an activity (creator-only)."""
    activity = db.query(Activity).filter(Activity.id == activity_id).first()
    if not activity:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="ACTIVITY_NOT_FOUND")

    if activity.creator_id and activity.creator_id != current_teacher.id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="NOT_ACTIVITY_CREATOR")

    if payload.name is not None:
        activity.name = payload.name
    if payload.summary is not None:
        activity.summary = payload.summary
    if payload.tags is not None:
        activity.tags = list(payload.tags)
    if payload.content_json is not None:
        if not isinstance(payload.content_json, dict):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="CONTENT_JSON_MUST_BE_OBJECT",
            )
        activity_type = (
            db.query(ActivityType).filter(ActivityType.type_name == activity.type).first()
        )
        if not activity_type:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="ACTIVITY_TYPE_MISSING",
            )
        _validate_activity_content(activity_type, payload.content_json)
        activity.content_json = dict(payload.content_json)

    db.commit()
    db.refresh(activity)
    return _activity_to_schema(activity)
