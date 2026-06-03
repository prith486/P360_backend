"""AI generation services for questions and assessment proposals."""

from __future__ import annotations

import json
from typing import Any, Iterable, Optional

import httpx
from sqlalchemy import func
from sqlalchemy.orm import Session

from app.core.config import settings
from app.models.enums import DifficultyLevel, QuestionType
from app.models.question import Question


def _strip_markdown_fences(raw_text: str) -> str:
    text = raw_text.strip()
    if text.startswith("```"):
        lines = text.splitlines()
        if lines and lines[0].startswith("```"):
            lines = lines[1:]
        if lines and lines[-1].strip().startswith("```"):
            lines = lines[:-1]
        text = "\n".join(lines).strip()
    return text


def _parse_json_array(raw_text: str) -> list[dict[str, Any]]:
    cleaned = _strip_markdown_fences(raw_text)
    try:
        parsed = json.loads(cleaned)
    except json.JSONDecodeError as exc:
        raise ValueError(f"AI response is not valid JSON: {exc}") from exc

    if not isinstance(parsed, list):
        raise ValueError("AI response must be a JSON array")

    normalized: list[dict[str, Any]] = []
    for item in parsed:
        if isinstance(item, dict):
            normalized.append(item)
        else:
            raise ValueError("AI response array contains a non-object item")

    return normalized


def _normalize_type(value: Any, fallback: str) -> str:
    q_type = str(value or fallback).strip().lower()
    if q_type in {"mcq", "coding"}:
        return q_type
    if q_type == "mixed":
        return fallback
    raise ValueError(f"Unsupported question type from AI: {q_type}")


def _normalize_difficulty(value: Any, fallback: str) -> str:
    difficulty = str(value or fallback).strip().lower()
    if difficulty not in {"easy", "medium", "hard", "expert"}:
        raise ValueError(f"Unsupported difficulty from AI: {difficulty}")
    return difficulty


def _normalize_mcq(item: dict[str, Any], fallback_difficulty: str) -> dict[str, Any]:
    question_text = str(item.get("question_text", "")).strip()
    if not question_text:
        raise ValueError("MCQ item missing question_text")

    options = item.get("options") or {}
    if not isinstance(options, dict):
        raise ValueError("MCQ item options must be an object")

    option_map = {
        "A": str(options.get("A", "")).strip(),
        "B": str(options.get("B", "")).strip(),
        "C": str(options.get("C", "")).strip(),
        "D": str(options.get("D", "")).strip(),
    }
    if not all(option_map.values()):
        raise ValueError("MCQ item requires options A/B/C/D")

    correct_option = str(item.get("correct_option", "")).strip().upper()
    if correct_option not in {"A", "B", "C", "D"}:
        raise ValueError("MCQ item has invalid correct_option")

    labels = ["A", "B", "C", "D"]
    formatted_options = []
    correct_index = None
    for idx, label in enumerate(labels, start=1):
        formatted_options.append(
            {
                "id": idx,
                "label": label,
                "text": option_map[label],
                "is_correct": label == correct_option,
            }
        )
        if label == correct_option:
            correct_index = idx

    return {
        "question_text": question_text,
        "type": "mcq",
        "difficulty": _normalize_difficulty(item.get("difficulty"), fallback_difficulty),
        "tags": item.get("tags") if isinstance(item.get("tags"), list) else [],
        "options": option_map,
        "formatted_options": formatted_options,
        "correct_option": correct_option,
        "solution_code": {"correct_option": correct_index},
        "explanation": item.get("explanation"),
        "time_estimate_minutes": int(item.get("time_estimate_minutes") or 3),
    }


def _normalize_coding(item: dict[str, Any], fallback_difficulty: str) -> dict[str, Any]:
    question_text = str(item.get("question_text", "")).strip()
    if not question_text:
        raise ValueError("Coding item missing question_text")

    starter_code = item.get("starter_code") if isinstance(item.get("starter_code"), dict) else {}
    normalized_starter = {
        "python": str(starter_code.get("python", "")).strip(),
        "cpp": str(starter_code.get("cpp", "")).strip(),
        "java": str(starter_code.get("java", "")).strip(),
    }

    raw_cases = item.get("sample_test_cases") if isinstance(item.get("sample_test_cases"), list) else []
    sample_test_cases: list[dict[str, str]] = []
    for case in raw_cases:
        if isinstance(case, dict):
            sample_test_cases.append(
                {
                    "input": str(case.get("input", "")).strip(),
                    "output": str(case.get("expected_output", case.get("output", ""))).strip(),
                }
            )

    return {
        "question_text": question_text,
        "type": "coding",
        "difficulty": _normalize_difficulty(item.get("difficulty"), fallback_difficulty),
        "tags": item.get("tags") if isinstance(item.get("tags"), list) else [],
        "starter_code": normalized_starter,
        "sample_test_cases": sample_test_cases,
        "explanation": item.get("explanation"),
        "time_estimate_minutes": int(item.get("time_estimate_minutes") or 15),
    }


def _build_generation_prompt(prompt_params: dict[str, Any]) -> tuple[str, str]:
    count = int(prompt_params.get("count", 1))
    topic = prompt_params.get("topic", "General Programming")
    difficulty = prompt_params.get("difficulty", "medium")
    question_type = prompt_params.get("question_type", "mixed")
    role_tags = prompt_params.get("role_tags") or []
    company_tags = prompt_params.get("company_tags") or []
    additional = prompt_params.get("additional_instructions") or ""

    system_prompt = (
        "You are an expert technical interviewer creating questions for a campus placement "
        "assessment platform. Generate high-quality and realistic interview questions. "
        "For each MCQ question return JSON object with: "
        "question_text, type='mcq', difficulty, tags (array), options object with A/B/C/D, "
        "correct_option, explanation, time_estimate_minutes. "
        "For each Coding question return JSON object with: question_text, type='coding', "
        "difficulty, tags (array), starter_code {python, cpp, java}, sample_test_cases "
        "([{input, expected_output}]), explanation, time_estimate_minutes. "
        "Return ONLY a valid JSON array. No markdown fences."
    )

    user_payload = {
        "topic": topic,
        "difficulty": difficulty,
        "question_type": question_type,
        "count": count,
        "role_tags": role_tags,
        "company_tags": company_tags,
        "additional_instructions": additional,
    }

    return system_prompt, json.dumps(user_payload)


def _call_openai_compatible(system_prompt: str, user_prompt: str) -> str:
    if not settings.OPENAI_API_KEY:
        raise ValueError("OPENAI_API_KEY is not configured")

    base_url = getattr(settings, "OPENAI_BASE_URL", "https://api.openai.com/v1")
    endpoint = f"{base_url.rstrip('/')}/chat/completions"

    payload = {
        "model": settings.OPENAI_MODEL,
        "messages": [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt},
        ],
        "temperature": 0.3,
    }

    headers = {
        "Authorization": f"Bearer {settings.OPENAI_API_KEY}",
        "Content-Type": "application/json",
    }

    with httpx.Client(timeout=120.0) as client:
        response = client.post(endpoint, json=payload, headers=headers)
        response.raise_for_status()
        body = response.json()

    choices = body.get("choices") or []
    if not choices:
        raise ValueError("OpenAI-compatible provider returned no choices")

    content = choices[0].get("message", {}).get("content")
    if not content:
        raise ValueError("OpenAI-compatible provider returned empty content")

    return content


def _call_anthropic(system_prompt: str, user_prompt: str) -> str:
    if not settings.ANTHROPIC_API_KEY:
        raise ValueError("ANTHROPIC_API_KEY is not configured")

    endpoint = "https://api.anthropic.com/v1/messages"
    payload = {
        "model": settings.ANTHROPIC_MODEL,
        "max_tokens": 4096,
        "temperature": 0.3,
        "system": system_prompt,
        "messages": [{"role": "user", "content": user_prompt}],
    }
    headers = {
        "x-api-key": settings.ANTHROPIC_API_KEY,
        "anthropic-version": "2023-06-01",
        "content-type": "application/json",
    }

    with httpx.Client(timeout=120.0) as client:
        response = client.post(endpoint, json=payload, headers=headers)
        response.raise_for_status()
        body = response.json()

    content_items = body.get("content") or []
    if not content_items:
        raise ValueError("Anthropic returned empty content")

    text = "".join(item.get("text", "") for item in content_items if isinstance(item, dict))
    if not text.strip():
        raise ValueError("Anthropic returned no text content")

    return text


def generate_questions(prompt_params: dict[str, Any]) -> list[dict[str, Any]]:
    """Generate question drafts from configured AI provider."""

    system_prompt, user_prompt = _build_generation_prompt(prompt_params)
    provider = str(settings.AI_PROVIDER).lower().strip()

    if provider == "openai":
        raw_text = _call_openai_compatible(system_prompt, user_prompt)
    elif provider in {"anthropic", "claude"}:
        raw_text = _call_anthropic(system_prompt, user_prompt)
    else:
        raise ValueError(f"Unsupported AI_PROVIDER: {settings.AI_PROVIDER}")

    parsed_items = _parse_json_array(raw_text)

    requested_type = str(prompt_params.get("question_type", "mixed")).lower()
    difficulty_input = prompt_params.get("difficulty", "medium")
    fallback_difficulty = difficulty_input[0] if isinstance(difficulty_input, list) and difficulty_input else difficulty_input
    fallback_difficulty = str(fallback_difficulty).lower()

    normalized: list[dict[str, Any]] = []
    for item in parsed_items:
        q_type = _normalize_type(item.get("type"), "mcq" if requested_type == "mcq" else "coding")
        if requested_type != "mixed" and q_type != requested_type:
            raise ValueError(f"AI returned {q_type} but {requested_type} was requested")

        if q_type == "mcq":
            normalized.append(_normalize_mcq(item, fallback_difficulty))
        else:
            normalized.append(_normalize_coding(item, fallback_difficulty))

    return normalized


def _question_type_matcher(mix: str) -> Iterable[QuestionType]:
    if mix == "mcq":
        return [QuestionType.MCQ]
    if mix == "coding":
        return [QuestionType.CODING]
    return [QuestionType.MCQ, QuestionType.CODING]


def _estimate_duration_for_bank_question(question: Question) -> int:
    return 3 if question.question_type == QuestionType.MCQ else 15


def _pick_from_bank(
    db: Session,
    topic: str,
    difficulty: str,
    allowed_types: list[QuestionType],
    required_count: int,
    excluded_ids: set[str],
    preferred_ids: set[str],
) -> list[Question]:
    if required_count <= 0:
        return []

    base_query = db.query(Question).filter(
        Question.is_active == True,  # noqa: E712
        Question.difficulty == DifficultyLevel(difficulty),
        Question.question_type.in_(allowed_types),
    )

    # JSONB array contains topic value.
    if topic:
        base_query = base_query.filter(Question.tags.contains([topic]))

    selected: list[Question] = []

    if preferred_ids:
        preferred_query = base_query.filter(Question.id.in_(preferred_ids))
        preferred_items = preferred_query.all()
        for item in preferred_items:
            item_id = str(item.id)
            if item_id in excluded_ids:
                continue
            selected.append(item)
            excluded_ids.add(item_id)
            if len(selected) >= required_count:
                return selected

    remaining = required_count - len(selected)
    if remaining <= 0:
        return selected

    fallback_items = base_query.order_by(func.random()).limit(remaining * 3).all()
    for item in fallback_items:
        item_id = str(item.id)
        if item_id in excluded_ids:
            continue
        selected.append(item)
        excluded_ids.add(item_id)
        if len(selected) >= required_count:
            break

    return selected


def generate_test(params: dict[str, Any], db: Session) -> dict[str, Any]:
    """Build a test proposal by filling from bank first and AI for deficits."""

    topic_distribution = params.get("topic_distribution") or []
    question_type_mix = str(params.get("question_type_mix", "mixed")).lower()
    existing_question_ids = {str(qid) for qid in (params.get("existing_question_ids") or [])}

    allowed_types = list(_question_type_matcher(question_type_mix))

    fulfilled_from_bank: list[dict[str, Any]] = []
    newly_generated: list[dict[str, Any]] = []
    unfilled_slots: list[dict[str, Any]] = []

    selected_ids: set[str] = set()
    estimated_duration = 0

    for slot in topic_distribution:
        topic = slot.get("topic")
        for difficulty in ["easy", "medium", "hard", "expert"]:
            requested = int(slot.get(difficulty, 0) or 0)
            if requested <= 0:
                continue

            picked = _pick_from_bank(
                db=db,
                topic=topic,
                difficulty=difficulty,
                allowed_types=allowed_types,
                required_count=requested,
                excluded_ids=selected_ids,
                preferred_ids=existing_question_ids,
            )

            for question in picked:
                fulfilled_from_bank.append(
                    {
                        "question_id": str(question.id),
                        "topic": topic,
                        "difficulty": difficulty,
                        "type": question.question_type.value,
                    }
                )
                estimated_duration += _estimate_duration_for_bank_question(question)

            deficit = requested - len(picked)
            if deficit <= 0:
                continue

            generation_type = question_type_mix if question_type_mix in {"mcq", "coding"} else "mixed"
            try:
                generated_batch = generate_questions(
                    {
                        "topic": topic,
                        "difficulty": difficulty,
                        "question_type": generation_type,
                        "count": deficit,
                        "additional_instructions": "Match requested slot exactly.",
                    }
                )
            except Exception as exc:
                unfilled_slots.append(
                    {
                        "topic": topic,
                        "difficulty": difficulty,
                        "requested": requested,
                        "filled": len(picked),
                        "reason": str(exc),
                    }
                )
                continue

            for question in generated_batch[:deficit]:
                newly_generated.append(
                    {
                        "question": question,
                        "topic": topic,
                        "difficulty": difficulty,
                        "type": question.get("type"),
                    }
                )
                estimated_duration += int(question.get("time_estimate_minutes") or (3 if question.get("type") == "mcq" else 15))

            still_unfilled = deficit - len(generated_batch)
            if still_unfilled > 0:
                unfilled_slots.append(
                    {
                        "topic": topic,
                        "difficulty": difficulty,
                        "requested": requested,
                        "filled": requested - still_unfilled,
                        "reason": "AI generated fewer items than requested",
                    }
                )

    total_questions = len(fulfilled_from_bank) + len(newly_generated)

    return {
        "fulfilled_from_bank": fulfilled_from_bank,
        "newly_generated": newly_generated,
        "unfilled_slots": unfilled_slots,
        "total_questions": total_questions,
        "estimated_duration_minutes": estimated_duration,
    }
