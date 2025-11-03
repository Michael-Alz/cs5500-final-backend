from __future__ import annotations

from typing import Any, Dict, List, Optional, Tuple

from sqlalchemy import func, or_
from sqlalchemy.orm import Session, joinedload

from app.core.config import settings
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

    platform_default = pick_system_default_activity(db)
    if platform_default:
        return "system-default", platform_default

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


SYSTEM_DEFAULT_ACTIVITY_TAG = "__system_default__"


def pick_system_default_activity(db: Session) -> Optional[Activity]:
    """Return the preferred system default activity according to env/tag/newest fallback."""
    env_id = settings.system_default_activity_id
    if env_id:
        activity = db.get(Activity, env_id)
        if activity:
            return activity

    activities = db.query(Activity).order_by(Activity.updated_at.desc()).all()
    if not activities:
        return None

    for activity in activities:
        tags = activity.tags or []
        if isinstance(tags, list) and SYSTEM_DEFAULT_ACTIVITY_TAG in tags:
            return activity

    return activities[0]


def _nullish_filter(field):
    return or_(field.is_(None), field == "")


def ensure_course_global_default(db: Session, course_id: str) -> None:
    """Ensure (None, None) recommendation exists and tracks the system default activity."""
    activity = pick_system_default_activity(db)
    if not activity:
        return

    recommendation = (
        db.query(CourseRecommendation)
        .filter(CourseRecommendation.course_id == course_id)
        .filter(_nullish_filter(CourseRecommendation.learning_style))
        .filter(_nullish_filter(CourseRecommendation.mood))
        .first()
    )

    if recommendation:
        if recommendation.is_auto and recommendation.activity_id != activity.id:
            recommendation.activity_id = activity.id
        if recommendation.is_auto:
            recommendation.is_auto = True
    else:
        db.add(
            CourseRecommendation(
                course_id=course_id,
                learning_style=None,
                mood=None,
                activity_id=activity.id,
                is_auto=True,
            )
        )
    db.flush()


def ensure_mood_defaults(
    db: Session, course_id: str, patched_pairs: List[Tuple[Optional[str], Optional[str], str]]
) -> None:
    """Ensure (None, mood) defaults follow the latest precise mappings."""
    latest_for_mood: dict[str, str] = {}
    for style, mood, activity_id in patched_pairs:
        if mood is None:
            continue
        latest_for_mood[mood] = activity_id

    for mood, activity_id in latest_for_mood.items():
        recommendation = (
            db.query(CourseRecommendation)
            .filter(CourseRecommendation.course_id == course_id)
            .filter(_nullish_filter(CourseRecommendation.learning_style))
            .filter(CourseRecommendation.mood == mood)
            .first()
        )
        if recommendation:
            if recommendation.is_auto and recommendation.activity_id != activity_id:
                recommendation.activity_id = activity_id
            if recommendation.is_auto:
                recommendation.is_auto = True
        else:
            db.add(
                CourseRecommendation(
                    course_id=course_id,
                    learning_style=None,
                    mood=mood,
                    activity_id=activity_id,
                    is_auto=True,
                )
            )
    db.flush()


def ensure_style_defaults(
    db: Session, course_id: str, patched_pairs: List[Tuple[Optional[str], Optional[str], str]]
) -> None:
    """Ensure (style, None) defaults follow the latest precise mappings."""
    latest_for_style: dict[str, str] = {}
    for style, mood, activity_id in patched_pairs:
        if style is None:
            continue
        latest_for_style[style] = activity_id

    for style, activity_id in latest_for_style.items():
        recommendation = (
            db.query(CourseRecommendation)
            .filter(CourseRecommendation.course_id == course_id)
            .filter(CourseRecommendation.learning_style == style)
            .filter(_nullish_filter(CourseRecommendation.mood))
            .first()
        )
        if recommendation:
            if recommendation.is_auto and recommendation.activity_id != activity_id:
                recommendation.activity_id = activity_id
            if recommendation.is_auto:
                recommendation.is_auto = True
        else:
            db.add(
                CourseRecommendation(
                    course_id=course_id,
                    learning_style=style,
                    mood=None,
                    activity_id=activity_id,
                    is_auto=True,
                )
            )
    db.flush()


def ensure_defaults_for_course(
    db: Session, course_id: str, patched_pairs: List[Tuple[Optional[str], Optional[str], str]]
) -> None:
    """Ensure auto-default recommendations exist without overwriting manual entries."""
    ensure_course_global_default(db, course_id)
    if patched_pairs:
        ensure_mood_defaults(db, course_id, patched_pairs)
        ensure_style_defaults(db, course_id, patched_pairs)
