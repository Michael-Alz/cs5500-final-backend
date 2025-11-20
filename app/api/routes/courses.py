from typing import List, Optional, Sequence

from fastapi import APIRouter, Body, Depends, HTTPException, Response, status
from sqlalchemy import and_, or_
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session, joinedload

from app.api.deps import get_current_teacher
from app.db import get_db
from app.models.activity import Activity
from app.models.course import Course
from app.models.course_recommendation import CourseRecommendation
from app.models.survey_template import SurveyTemplate
from app.models.teacher import Teacher
from app.schemas.course import (
    CourseAutoRecommendationRequest,
    CourseCreate,
    CourseOut,
    CourseRecommendationActivity,
    CourseRecommendationMapping,
    CourseRecommendationOutItem,
    CourseRecommendationsOut,
    CourseRecommendationsPatchIn,
    CourseUpdate,
)
from app.services.ai_recommendations import generate_ai_recommendations
from app.services.recommendations import ensure_defaults_for_course
from app.services.surveys import extract_learning_style_categories

router = APIRouter()


def _normalize_mood_labels(mood_labels: List[str]) -> List[str]:
    """Clean and deduplicate mood labels."""
    cleaned: list[str] = []
    for label in mood_labels:
        trimmed = label.strip()
        if not trimmed:
            continue
        if trimmed not in cleaned:
            cleaned.append(trimmed)
    if not cleaned:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="MOOD_LABELS_REQUIRED",
        )
    return cleaned


def _normalize_key(value: Optional[str]) -> Optional[str]:
    """Convert wildcard or empty values into None."""
    if value is None:
        return None
    trimmed = value.strip()
    if trimmed == "" or trimmed in {"*", "any", "ANY", "default"}:
        return None
    return trimmed


def _get_course_or_404(
    db: Session, course_id: str, teacher: Teacher, *, eager_recommendations: bool = False
) -> Course:
    """Fetch a course ensuring ownership."""
    query = db.query(Course).filter(and_(Course.id == course_id, Course.teacher_id == teacher.id))
    if eager_recommendations:
        query = query.options(
            joinedload(Course.recommendations).joinedload(CourseRecommendation.activity)
        )
    course = query.first()
    if not course:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="COURSE_NOT_FOUND")
    return course


def _survey_categories(template: SurveyTemplate) -> List[str]:
    """Extract learning style categories from survey template."""
    questions: list[dict] = template.questions_json or []
    return extract_learning_style_categories(questions)


def _course_to_schema(course: Course) -> CourseOut:
    return CourseOut.model_validate(
        course,
        from_attributes=True,
    )


def _apply_recommendation_mappings(
    db: Session,
    course: Course,
    mappings: Sequence[CourseRecommendationMapping],
    *,
    mark_auto: bool,
    allow_overwrite_manual: bool,
) -> List[tuple[Optional[str], Optional[str], str]]:
    """Persist recommendation mappings with validation and optional overwrite rules."""
    patched_pairs: list[tuple[Optional[str], Optional[str], str]] = []
    for mapping in mappings:
        learning_style = _normalize_key(mapping.learning_style)
        mood = _normalize_key(mapping.mood)

        if learning_style and learning_style not in (course.learning_style_categories or []):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"UNKNOWN_LEARNING_STYLE:{learning_style}",
            )
        if mood and mood not in (course.mood_labels or []):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"UNKNOWN_MOOD:{mood}",
            )

        activity = db.query(Activity).filter(Activity.id == mapping.activity_id).first()
        if not activity:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"ACTIVITY_NOT_FOUND:{mapping.activity_id}",
            )

        existing_query = db.query(CourseRecommendation).filter(
            CourseRecommendation.course_id == course.id
        )
        if learning_style is None:
            existing_query = existing_query.filter(
                or_(
                    CourseRecommendation.learning_style.is_(None),
                    CourseRecommendation.learning_style == "",
                )
            )
        else:
            existing_query = existing_query.filter(
                CourseRecommendation.learning_style == learning_style
            )

        if mood is None:
            existing_query = existing_query.filter(
                or_(CourseRecommendation.mood.is_(None), CourseRecommendation.mood == "")
            )
        else:
            existing_query = existing_query.filter(CourseRecommendation.mood == mood)

        recommendation = existing_query.first()
        if recommendation:
            if not allow_overwrite_manual and not recommendation.is_auto:
                continue
            recommendation.activity_id = activity.id
            recommendation.is_auto = mark_auto
        else:
            recommendation = CourseRecommendation(
                course_id=course.id,
                learning_style=learning_style,
                mood=mood,
                activity_id=activity.id,
                is_auto=mark_auto,
            )
            db.add(recommendation)
        patched_pairs.append((learning_style, mood, str(activity.id)))
    return patched_pairs


@router.post("/", response_model=CourseOut, status_code=status.HTTP_201_CREATED)
def create_course(
    course_data: CourseCreate,
    db: Session = Depends(get_db),
    current_teacher: Teacher = Depends(get_current_teacher),
) -> CourseOut:
    """Create a new course with baseline survey and mood labels."""
    template = (
        db.query(SurveyTemplate).filter(SurveyTemplate.id == course_data.baseline_survey_id).first()
    )
    if not template:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="SURVEY_TEMPLATE_NOT_FOUND",
        )

    mood_labels = _normalize_mood_labels(course_data.mood_labels)
    categories = _survey_categories(template)

    try:
        course = Course(
            title=course_data.title,
            teacher_id=current_teacher.id,
            baseline_survey_id=template.id,
            learning_style_categories=categories,
            mood_labels=mood_labels,
            requires_rebaseline=True,
        )
        db.add(course)
        db.commit()
        db.refresh(course)
        ensure_defaults_for_course(db, course.id, [])
        if db.new or db.dirty:
            db.commit()
            db.refresh(course)
        return _course_to_schema(course)
    except IntegrityError as exc:
        db.rollback()
        if "uq_course_title_per_teacher" in str(exc.orig):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="COURSE_TITLE_EXISTS",
            )
        raise


@router.get("/", response_model=List[CourseOut])
def list_courses(
    db: Session = Depends(get_db), current_teacher: Teacher = Depends(get_current_teacher)
) -> List[CourseOut]:
    """List all courses for the authenticated teacher."""
    courses = db.query(Course).filter(Course.teacher_id == current_teacher.id).all()
    return [_course_to_schema(course) for course in courses]


@router.get("/{course_id}", response_model=CourseOut)
def get_course(
    course_id: str,
    db: Session = Depends(get_db),
    current_teacher: Teacher = Depends(get_current_teacher),
) -> CourseOut:
    """Fetch a single course for the authenticated teacher."""
    course = db.query(Course).filter(Course.id == course_id).first()
    if course is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="COURSE_NOT_FOUND",
        )
    if course.teacher_id != current_teacher.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="COURSE_ACCESS_DENIED",
        )
    return _course_to_schema(course)


@router.patch("/{course_id}", response_model=CourseOut)
def update_course(
    course_id: str,
    updates: CourseUpdate,
    db: Session = Depends(get_db),
    current_teacher: Teacher = Depends(get_current_teacher),
) -> CourseOut:
    """Update mutable course fields (title, baseline survey)."""
    course = _get_course_or_404(db, course_id, current_teacher)

    if updates.title is not None:
        course.title = updates.title

    if (
        updates.baseline_survey_id is not None
        and updates.baseline_survey_id != course.baseline_survey_id
    ):
        template = (
            db.query(SurveyTemplate).filter(SurveyTemplate.id == updates.baseline_survey_id).first()
        )
        if not template:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="SURVEY_TEMPLATE_NOT_FOUND",
            )

        categories = _survey_categories(template)
        course.baseline_survey_id = template.id
        course.learning_style_categories = categories
        course.requires_rebaseline = True

    db.commit()
    db.refresh(course)
    return _course_to_schema(course)


@router.delete("/{course_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_course(
    course_id: str,
    db: Session = Depends(get_db),
    current_teacher: Teacher = Depends(get_current_teacher),
) -> Response:
    """Delete a course and all related records (sessions, submissions, mappings, profiles)."""
    course = _get_course_or_404(db, course_id, current_teacher)
    db.delete(course)
    db.commit()
    return Response(status_code=status.HTTP_204_NO_CONTENT)


def _serialize_recommendation_item(
    recommendation: CourseRecommendation,
) -> CourseRecommendationOutItem:
    activity = recommendation.activity
    activity_payload = None
    if activity:
        activity_payload = CourseRecommendationActivity(
            activity_id=str(activity.id),
            name=str(activity.name),
            summary=str(activity.summary),
            type=str(activity.type),
            content_json=dict(activity.content_json or {}),
        )
    return CourseRecommendationOutItem(
        learning_style=recommendation.learning_style or None,
        mood=recommendation.mood or None,
        activity=activity_payload,
    )


@router.get("/{course_id}/recommendations", response_model=CourseRecommendationsOut)
def get_course_recommendations(
    course_id: str,
    db: Session = Depends(get_db),
    current_teacher: Teacher = Depends(get_current_teacher),
) -> CourseRecommendationsOut:
    """Fetch recommendation mappings for a course."""
    course = _get_course_or_404(db, course_id, current_teacher, eager_recommendations=True)
    items = [
        _serialize_recommendation_item(recommendation) for recommendation in course.recommendations
    ]
    return CourseRecommendationsOut(
        course_id=str(course.id),
        learning_style_categories=list(course.learning_style_categories or []),
        mood_labels=list(course.mood_labels or []),
        mappings=items,
    )


@router.patch("/{course_id}/recommendations", response_model=CourseRecommendationsOut)
def upsert_course_recommendations(
    course_id: str,
    payload: CourseRecommendationsPatchIn,
    db: Session = Depends(get_db),
    current_teacher: Teacher = Depends(get_current_teacher),
) -> CourseRecommendationsOut:
    """Upsert recommendation mappings for a course."""
    course = _get_course_or_404(db, course_id, current_teacher)

    patched_pairs = _apply_recommendation_mappings(
        db,
        course,
        payload.mappings,
        mark_auto=False,
        allow_overwrite_manual=True,
    )
    ensure_defaults_for_course(db, course.id, patched_pairs)
    db.commit()

    refreshed = _get_course_or_404(db, course_id, current_teacher, eager_recommendations=True)
    return CourseRecommendationsOut(
        course_id=str(refreshed.id),
        learning_style_categories=list(refreshed.learning_style_categories or []),
        mood_labels=list(refreshed.mood_labels or []),
        mappings=[_serialize_recommendation_item(rec) for rec in refreshed.recommendations],
    )


@router.post(
    "/{course_id}/recommendations/auto",
    response_model=CourseRecommendationsPatchIn,
    status_code=status.HTTP_200_OK,
)
async def auto_generate_course_recommendations(
    course_id: str,
    payload: CourseAutoRecommendationRequest = Body(
        default_factory=CourseAutoRecommendationRequest
    ),
    db: Session = Depends(get_db),
    current_teacher: Teacher = Depends(get_current_teacher),
) -> CourseRecommendationsOut:
    """Generate recommendation mappings using OpenRouter AI and persist auto selections."""
    course = _get_course_or_404(db, course_id, current_teacher)

    learning_styles = list(course.learning_style_categories or [])
    mood_labels = list(course.mood_labels or [])

    activity_query = db.query(Activity).order_by(Activity.updated_at.desc())
    activity_query = activity_query.limit(payload.activity_limit)
    activities = activity_query.all()

    ai_mappings = await generate_ai_recommendations(
        course_title=course.title,
        learning_styles=learning_styles,
        mood_labels=mood_labels,
        activities=activities,
        request=payload,
    )

    if not ai_mappings:
        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail="AI_RECOMMENDER_EMPTY_RESPONSE",
        )

    return CourseRecommendationsPatchIn(mappings=ai_mappings)
