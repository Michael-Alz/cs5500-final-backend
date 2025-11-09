from __future__ import annotations

import json
from typing import Any, Optional, Sequence

import httpx
from fastapi import HTTPException, status
from pydantic import ValidationError

from app.core.config import settings
from app.models.activity import Activity
from app.schemas.course import (
    CourseAutoRecommendationRequest,
    CourseRecommendationMapping,
    CourseRecommendationsPatchIn,
)

OPENROUTER_TIMEOUT_SECONDS = 30.0


def _activity_payload(activity: Activity) -> dict[str, Any]:
    return {
        "activity_id": str(activity.id),
        "name": str(activity.name),
        "summary": str(activity.summary),
        "type": str(activity.type),
        "tags": list(activity.tags or []),
        "content_json": dict(activity.content_json or {}),
    }


def _build_user_prompt(
    *,
    course_title: str,
    learning_styles: Sequence[str],
    mood_labels: Sequence[str],
    activities_payload: Sequence[dict[str, Any]],
) -> str:
    return (
        "You are a classroom strategy assistant.\n\n"
        f"Course title: {course_title}\n"
        "Here is background information about the students:\n"
        f"- Known learning styles: {json.dumps(list(learning_styles), ensure_ascii=False)}\n"
        f"- Known moods: {json.dumps(list(mood_labels), ensure_ascii=False)}\n\n"
        "Here is a list of available pre-class activities in JSON array format.\n"
        "Each activity has the following fields:\n"
        "name, summary, type, tags, content_json, id, creator_id, creator_name, "
        "creator_email, created_at, updated_at.\n\n"
        "Available activities (JSON array):\n"
        f"{json.dumps(list(activities_payload), ensure_ascii=False, indent=2)}\n\n"
        "Task:\n"
        "For every combination of learning style and mood (total = number of learning styles * "
        "number of moods), choose the most suitable activity based on its name, summary, type, "
        "tags, and content_json.\n\n"
        "If no activity clearly fits a specific combination, choose the one that has the tag "
        '"__system_default__".\n\n'
        "Output format:\n"
        "Return only a valid JSON object in this format:\n"
        "{\n"
        '"mappings": [\n'
        "{\n"
        '"learning_style": "string",\n'
        '"mood": "string",\n'
        '"activity_id": "string"\n'
        "}\n"
        "]\n"
        "}\n\n"
        "Notes:\n"
        '- The length of the "mappings" array must equal the total number of combinations '
        "(len(learning_styles) * len(moods)).\n"
        '- The "activity_id" should correspond to the most relevant activity for that pair.\n'
        "- Do not include explanations, comments, or any text outside the JSON.\n"
    )


async def generate_ai_recommendations(
    *,
    course_title: str,
    learning_styles: Sequence[str],
    mood_labels: Sequence[str],
    activities: Sequence[Activity],
    request: CourseAutoRecommendationRequest,
) -> list[CourseRecommendationMapping]:
    if not settings.openrouter_api_key:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="AI_RECOMMENDER_NOT_CONFIGURED",
        )

    if not activities:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="NO_ACTIVITIES_AVAILABLE",
        )

    styles = list(learning_styles)
    moods = list(mood_labels)
    activities_payload = [
        _activity_payload(activity) for activity in activities[: request.activity_limit]
    ]
    prompt = _build_user_prompt(
        course_title=course_title,
        learning_styles=styles,
        mood_labels=moods,
        activities_payload=activities_payload,
    )

    model_name = request.model or settings.openrouter_default_model
    payload = {
        "model": model_name,
        "messages": [
            {"role": "user", "content": prompt},
        ],
        "temperature": request.temperature,
    }

    headers = {
        "Authorization": f"Bearer {settings.openrouter_api_key}",
        "Content-Type": "application/json",
        "HTTP-Referer": settings.public_app_url,
        "X-Title": settings.app_name,
    }

    try:
        async with httpx.AsyncClient(timeout=OPENROUTER_TIMEOUT_SECONDS) as client:
            response = await client.post(
                settings.openrouter_api_base,
                headers=headers,
                json=payload,
            )
            response.raise_for_status()
    except httpx.HTTPStatusError as exc:
        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail="AI_RECOMMENDER_BAD_RESPONSE",
        ) from exc
    except httpx.RequestError as exc:
        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail="AI_RECOMMENDER_UNAVAILABLE",
        ) from exc

    try:
        data = response.json()
    except ValueError as exc:
        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail="AI_RECOMMENDER_INVALID_JSON",
        ) from exc
    try:
        content = data["choices"][0]["message"]["content"]
    except (KeyError, IndexError, TypeError) as exc:
        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail="AI_RECOMMENDER_EMPTY_RESPONSE",
        ) from exc

    try:
        parsed = json.loads(content)
    except json.JSONDecodeError as exc:
        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail="AI_RECOMMENDER_INVALID_JSON",
        ) from exc

    # Some model responses might omit the root object and return a bare list
    if isinstance(parsed, list):
        parsed = {"mappings": parsed}

    if not isinstance(parsed, dict):
        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail="AI_RECOMMENDER_INVALID_PAYLOAD",
        )

    payload_key = None
    if isinstance(parsed, dict):
        if isinstance(parsed.get("mappings"), list):
            payload_key = "mappings"
        elif isinstance(parsed.get("recommendations"), list):
            payload_key = "recommendations"

    if payload_key is None:
        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail="AI_RECOMMENDER_INVALID_PAYLOAD",
        )

    try:
        validated = CourseRecommendationsPatchIn(mappings=parsed[payload_key])
    except ValidationError as exc:
        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail="AI_RECOMMENDER_SCHEMA_MISMATCH",
        ) from exc

    combos_expected = len(styles) * len(moods)
    mappings = list(validated.mappings)
    if combos_expected and len(mappings) != combos_expected:
        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail="AI_RECOMMENDER_INCOMPLETE_COMBINATIONS",
        )

    expected_pairs = {(style or None, mood or None) for style in styles for mood in moods}
    seen_pairs = {
        (_normalize_prompt_field(mapping.learning_style), _normalize_prompt_field(mapping.mood))
        for mapping in mappings
    }
    if combos_expected and seen_pairs != expected_pairs:
        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail="AI_RECOMMENDER_WRONG_COMBINATIONS",
        )

    return mappings


def _normalize_prompt_field(value: Optional[str]) -> Optional[str]:
    if value is None:
        return None
    trimmed = value.strip()
    if trimmed == "":
        return None
    return trimmed
