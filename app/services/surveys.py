from __future__ import annotations

from typing import Any, Dict, List, Optional


def extract_learning_style_categories(questions: List[dict[str, Any]]) -> List[str]:
    """Collect unique learning style categories from survey questions."""
    categories: set[str] = set()
    for question in questions:
        for option in question.get("options", []):
            scores = option.get("scores", {})
            for category in scores.keys():
                categories.add(str(category))
    return sorted(categories)


def build_survey_snapshot(template: Any) -> Dict[str, Any]:
    """Construct a survey snapshot for storing on sessions."""
    questions = []
    survey_id = None
    title = None

    if hasattr(template, "questions_json"):
        questions = getattr(template, "questions_json") or []
    elif isinstance(template, dict):
        questions = template.get("questions_json") or template.get("questions") or []
    else:
        questions = []

    if hasattr(template, "id"):
        survey_id = getattr(template, "id")
    elif isinstance(template, dict):
        survey_id = template.get("id")

    if hasattr(template, "title"):
        title = getattr(template, "title")
    elif isinstance(template, dict):
        title = template.get("title")

    return {
        "survey_id": survey_id,
        "title": title,
        "questions": questions,
    }


def compute_total_scores(
    survey_snapshot: Dict[str, Any], answers: Dict[str, str]
) -> Dict[str, int]:
    """Calculate aggregate scores for each learning style category."""
    questions: List[dict[str, Any]] = survey_snapshot.get("questions", [])
    categories = extract_learning_style_categories(questions)
    totals: Dict[str, int] = {category: 0 for category in categories}

    for question in questions:
        question_id = question.get("id") or question.get("question_id")
        if not question_id:
            continue

        selected_answer = answers.get(str(question_id))
        if not selected_answer:
            continue

        for index, option in enumerate(question.get("options", [])):
            option_id = option.get("id") or option.get("option_id") or option.get("value")
            if option_id is None:
                option_id = f"{question_id}_opt_{index}"
            option_label = option.get("label") or option.get("text")

            if selected_answer not in {str(option_id), str(option_label)}:
                continue

            for category, score in option.get("scores", {}).items():
                if category not in totals:
                    totals[category] = 0
                if isinstance(score, (int, float)):
                    totals[category] += int(score)
            break

    return totals


def determine_learning_style(total_scores: Dict[str, int]) -> Optional[str]:
    """Return the category with the highest score, breaking ties deterministically."""
    if not total_scores:
        return None

    best_category = None
    best_score = None

    for category, score in total_scores.items():
        if (
            best_score is None
            or score > best_score
            or (score == best_score and category < (best_category or category))
        ):
            best_category = category
            best_score = score

    return best_category


def snapshot_to_public_payload(snapshot: Optional[Dict[str, Any]]) -> Optional[Dict[str, Any]]:
    """Produce a student-friendly snapshot payload."""
    if not snapshot:
        return None

    questions_payload: List[Dict[str, Any]] = []
    questions: List[dict[str, Any]] = snapshot.get("questions", [])
    for question in questions:
        question_id = question.get("id") or question.get("question_id")
        if not question_id:
            continue

        options_payload: List[Dict[str, Any]] = []
        options = question.get("options", [])
        for idx, option in enumerate(options):
            option_id = option.get("id") or option.get("option_id")
            if option_id is None:
                option_id = f"{question_id}_opt_{idx}"
            option_text = option.get("text") or option.get("label") or str(option_id)
            options_payload.append(
                {
                    "option_id": str(option_id),
                    "text": str(option_text),
                }
            )

        questions_payload.append(
            {
                "question_id": str(question_id),
                "text": str(question.get("text") or question.get("question") or question_id),
                "options": options_payload,
            }
        )

    return {
        "survey_id": snapshot.get("survey_id"),
        "title": snapshot.get("title"),
        "questions": questions_payload,
    }


def build_answer_details(
    survey_snapshot: Dict[str, Any], answers: Dict[str, str]
) -> Dict[str, Any]:
    """Return a per-question mapping that includes question/option text for the chosen answers."""
    details: Dict[str, Any] = {}
    questions: List[dict[str, Any]] = survey_snapshot.get("questions", [])

    for question_index, question in enumerate(questions):
        question_id = question.get("id") or question.get("question_id")
        if not question_id:
            continue

        selected = answers.get(str(question_id))
        if not selected:
            continue

        question_text = question.get("text") or question.get("question") or str(question_id)
        selected_option_id = None
        selected_option_text = None
        options_detail: List[Dict[str, str]] = []

        for option_index, option in enumerate(question.get("options", [])):
            option_id = option.get("id") or option.get("option_id") or option.get("value")
            if option_id is None:
                option_id = f"{question_id}_opt_{option_index}"
            option_text = option.get("text") or option.get("label") or str(option_id)
            option_id_str = str(option_id)
            options_detail.append({"option_id": option_id_str, "text": str(option_text)})

            if str(selected) in {option_id_str, str(option_text)}:
                selected_option_id = option_id_str
                selected_option_text = str(option_text)

        if selected_option_id:
            details[str(question_id)] = {
                "question_id": str(question_id),
                "question_text": str(question_text),
                "selected_option_id": selected_option_id,
                "selected_option_text": selected_option_text,
                "options": options_detail,
            }

    return details
