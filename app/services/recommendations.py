from __future__ import annotations

from typing import Any, Dict, Optional, Tuple

from sqlalchemy import func, or_
from sqlalchemy.orm import Session, joinedload

from app.models.activity import Activity
from app.models.course_recommendation import CourseRecommendation


def _normalize_default(value: Optional[str]) -> Optional[str]:
    """Treat special tokens as defaults (None)."""
    if value is None:
        return None
    trimmed = value.strip()
    if trimmed == "":
        return None
    if trimmed in {"*", "ANY", "any", "default"}:
        return None
    return value


def _query_recommendation(
    db: Session,
    course_id: str,
    learning_style: Optional[str],
    mood: Optional[str],
    randomize: bool = False,
) -> Optional[CourseRecommendation]:
    """Helper to query recommendation with optional random ordering."""
    query = (
        db.query(CourseRecommendation)
        .options(joinedload(CourseRecommendation.activity))
        .filter(CourseRecommendation.course_id == course_id)
    )

    normalized_style = _normalize_default(learning_style)
    normalized_mood = _normalize_default(mood)

    if normalized_style is None:
        query = query.filter(
            or_(
                CourseRecommendation.learning_style.is_(None),
                CourseRecommendation.learning_style == "",
            )
        )
    else:
        query = query.filter(CourseRecommendation.learning_style == normalized_style)

    if normalized_mood is None:
        query = query.filter(
            or_(CourseRecommendation.mood.is_(None), CourseRecommendation.mood == "")
        )
    else:
        query = query.filter(CourseRecommendation.mood == normalized_mood)

    if randomize:
        query = query.order_by(func.random())
    else:
        query = query.order_by(CourseRecommendation.updated_at.desc())

    return query.first()


def get_recommended_activity(
    db: Session, course_id: str, mood: str, learning_style: Optional[str]
) -> Tuple[str, Optional[Activity]]:
    """Return the best matching activity according to fallback priority."""
    # Priority 1: exact learning_style + mood
    if learning_style:
        exact_match = _query_recommendation(db, course_id, learning_style, mood)
        if exact_match and exact_match.activity:
            return "style+mood", exact_match.activity

        # Priority 2: style default
        style_default = _query_recommendation(db, course_id, learning_style, None)
        if style_default and style_default.activity:
            return "style-default", style_default.activity

    # Priority 3: mood default (style unknown or no style match)
    mood_default = _query_recommendation(db, course_id, None, mood)
    if mood_default and mood_default.activity:
        return "mood-default", mood_default.activity

    # Priority 4: random course activity (any mapping)
    random_pick = _query_recommendation(db, course_id, None, None, randomize=True)
    if random_pick and random_pick.activity:
        return "random-course-activity", random_pick.activity

    return "none", None


def build_recommended_activity_payload(
    match_type: str,
    mood: str,
    learning_style: Optional[str],
    activity: Optional[Activity],
) -> Dict[str, Any]:
    """Convert recommendation data into a serialisable payload."""
    activity_payload: Optional[Dict[str, Any]] = None
    if activity:
        activity_payload = {
            "activity_id": str(activity.id),
            "name": str(activity.name),
            "summary": str(activity.summary),
            "type": str(activity.type),
            "content_json": dict(activity.content_json or {}),
        }

    return {
        "match_type": match_type,
        "learning_style": learning_style,
        "mood": mood,
        "activity": activity_payload,
    }
