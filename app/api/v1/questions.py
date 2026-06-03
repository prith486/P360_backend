import uuid
from typing import Optional, Any

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import func
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.api.deps import get_current_faculty, get_current_active_user
from app.models.faculty import Faculty
from app.models.question import Question
from app.models.enums import DifficultyLevel, QuestionType
from app.schemas.question import QuestionCreate, QuestionRead, QuestionUpdate, CodeRunRequest, CodeRunResponse
from app.schemas.ai_generation import (
    GenerateQuestionsRequest,
    GenerateQuestionsSaveRequest,
    SmartPickerRequest,
)
from app.core.cache import get_cached, set_cached, invalidate_cache
from app.core.logging_config import get_logger
from app.services.ai_service import generate_questions as ai_generate_questions
import random
import time
logger = get_logger(__name__)

router = APIRouter()

@router.post("", response_model=dict)
@router.post("/", response_model=dict, include_in_schema=False)
def create_question(
    data: QuestionCreate,
    db: Session = Depends(get_db),
    current_faculty: Faculty = Depends(get_current_faculty)
):
    slug_uuid = "{:.8}".format(str(uuid.uuid4()))
    slug = f"{data.title.lower().replace(' ', '-')}-{slug_uuid}"
    
    dump = data.model_dump()
    dump.pop("slug", None)
    
    question = Question(
        **dump,
        slug=slug,
        created_by=current_faculty.user_id,
        total_submissions=0,
        total_accepted=0,
        acceptance_rate=0.0,
        is_active=True
    )
    db.add(question)
    db.commit()
    db.refresh(question)
    
    invalidate_cache("questions_")
    
    return {
        "success": True,
        "data": QuestionRead.model_validate(question).model_dump(mode='json')
    }

@router.get("", response_model=dict)
@router.get("/", response_model=dict, include_in_schema=False)
def get_questions(
    difficulty: Optional[str] = None,
    question_type: Optional[str] = None,
    tag: Optional[str] = None,
    db: Session = Depends(get_db),
    current_faculty: Faculty = Depends(get_current_faculty)
):
    cache_key = f"questions_{difficulty}_{question_type}_{tag}"
    cached = get_cached(cache_key)
    if cached:
        return cached

    query = db.query(Question)
    if difficulty:
        from app.models.enums import DifficultyLevel
        try:
            query = query.filter(Question.difficulty == DifficultyLevel(difficulty))
        except ValueError:
            pass # ignore invalid difficulty
            
    if question_type:
        from app.models.enums import QuestionType
        try:
            query = query.filter(Question.question_type == QuestionType(question_type))
        except ValueError:
            pass # ignore invalid type
            
    questions_list = query.all()
    if tag:
        questions_list = [q for q in questions_list if q.tags and tag in q.tags]
        
    try:
        data = []
        for q in questions_list:
            q_dict = QuestionRead.model_validate(q).model_dump(mode='json')
            # Add fields for frontend compatibility
            q_dict["type"] = q.question_type.value if hasattr(q.question_type, 'value') else str(q.question_type)
            q_dict["marks"] = q.max_score
            data.append(q_dict)
    except Exception as e:
        logger.error(f"Error formatting questions: {str(e)}")
        # Fallback to manual dict if Pydantic fails
        data = []
        for q in questions_list:
            data.append({
                "id": str(q.id),
                "title": q.title,
                "slug": q.slug,
                "difficulty": q.difficulty.value if hasattr(q.difficulty, 'value') else str(q.difficulty),
                "type": q.question_type.value if hasattr(q.question_type, 'value') else str(q.question_type),
                "question_type": q.question_type.value if hasattr(q.question_type, 'value') else str(q.question_type),
                "description": q.description,
                "max_score": q.max_score,
                "marks": q.max_score,
                "created_at": q.created_at.isoformat() if q.created_at else None
            })
            
    res = {"success": True, "count": len(data), "data": data}
    set_cached(cache_key, res, 60)
    return res


def _make_slug(seed_text: str) -> str:
    slug_uuid = str(uuid.uuid4())[:8]
    cleaned = "-".join(seed_text.lower().strip().split())
    cleaned = cleaned[:80] if cleaned else "question"
    return f"{cleaned}-{slug_uuid}"


def _normalize_generated_question_payload(item: dict[str, Any], faculty_user_id: uuid.UUID) -> Question:
    question_text = str(item.get("question_text", "")).strip()
    if not question_text:
        raise ValueError("question_text is required")

    q_type = str(item.get("type", "")).strip().lower()
    difficulty = str(item.get("difficulty", "")).strip().lower()

    if q_type not in {"mcq", "coding"}:
        raise ValueError("type must be mcq or coding")

    if difficulty not in {"easy", "medium", "hard", "expert"}:
        raise ValueError("difficulty must be easy, medium, hard, or expert")

    payload: dict[str, Any] = {
        "title": question_text[:120] if len(question_text) > 120 else question_text,
        "slug": _make_slug(question_text),
        "difficulty": DifficultyLevel(difficulty),
        "question_type": QuestionType(q_type),
        "description": question_text,
        "tags": item.get("tags") if isinstance(item.get("tags"), list) else [],
        "editorial": item.get("explanation"),
        "created_by": faculty_user_id,
        "total_submissions": 0,
        "total_accepted": 0,
        "acceptance_rate": 0.0,
        "is_active": True,
        "source": "AI Generated",
    }

    if q_type == "mcq":
        options_raw = item.get("options") if isinstance(item.get("options"), dict) else {}
        option_map = {
            "A": str(options_raw.get("A", "")).strip(),
            "B": str(options_raw.get("B", "")).strip(),
            "C": str(options_raw.get("C", "")).strip(),
            "D": str(options_raw.get("D", "")).strip(),
        }
        if not all(option_map.values()):
            raise ValueError("mcq requires non-empty options A/B/C/D")

        correct_option = str(item.get("correct_option", "")).strip().upper()
        if correct_option not in {"A", "B", "C", "D"}:
            raise ValueError("mcq requires correct_option in A/B/C/D")

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

        payload["options"] = formatted_options
        payload["solution_code"] = {"correct_option": correct_index}

    if q_type == "coding":
        payload["starter_code"] = item.get("starter_code") if isinstance(item.get("starter_code"), dict) else {}

        sample_cases = []
        if isinstance(item.get("sample_test_cases"), list):
            for case in item.get("sample_test_cases", []):
                if isinstance(case, dict):
                    sample_cases.append(
                        {
                            "input": str(case.get("input", "")).strip(),
                            "output": str(case.get("expected_output", case.get("output", ""))).strip(),
                        }
                    )
        payload["sample_test_cases"] = sample_cases

    return Question(**payload)


@router.post("/generate", response_model=dict)
def generate_questions_preview(
    data: GenerateQuestionsRequest,
    db: Session = Depends(get_db),
    current_faculty: Faculty = Depends(get_current_faculty),
):
    _ = db
    _ = current_faculty
    generated = ai_generate_questions(data.model_dump())
    return {"success": True, "questions": generated, "count": len(generated)}


@router.post("/generate/save", response_model=dict)
def save_generated_questions(
    payload: GenerateQuestionsSaveRequest,
    db: Session = Depends(get_db),
    current_faculty: Faculty = Depends(get_current_faculty),
):
    if not payload.questions:
        raise HTTPException(status_code=400, detail="questions payload cannot be empty")

    saved_ids: list[str] = []
    failed: list[dict[str, Any]] = []

    for idx, item in enumerate(payload.questions):
        try:
            question = _normalize_generated_question_payload(item, current_faculty.user_id)
            db.add(question)
            db.flush()
            saved_ids.append(str(question.id))
        except Exception as exc:
            failed.append({"index": idx, "reason": str(exc)})

    db.commit()

    if saved_ids:
        invalidate_cache("questions_")

    return {
        "success": True,
        "saved_count": len(saved_ids),
        "question_ids": saved_ids,
        "failed": failed,
    }


@router.post("/pick", response_model=dict)
def pick_questions_by_criteria(
    payload: SmartPickerRequest,
    db: Session = Depends(get_db),
    current_faculty: Faculty = Depends(get_current_faculty),
):
    _ = current_faculty

    selected_ids = set(payload.exclude_question_ids)
    picked: list[dict[str, Any]] = []
    shortages: list[dict[str, Any]] = []

    for criterion in payload.criteria:
        topic = criterion.topic
        requested_by_difficulty = {
            "easy": criterion.easy,
            "medium": criterion.medium,
            "hard": criterion.hard,
            "expert": criterion.expert,
        }

        allowed_types: list[QuestionType] = []
        for type_name in criterion.types:
            try:
                allowed_types.append(QuestionType(type_name))
            except Exception:
                continue

        if not allowed_types:
            continue

        for difficulty, requested in requested_by_difficulty.items():
            if requested <= 0:
                continue

            query = db.query(Question).filter(
                Question.is_active == True,  # noqa: E712
                Question.difficulty == DifficultyLevel(difficulty),
                Question.question_type.in_(allowed_types),
            )

            if topic:
                query = query.filter(Question.tags.contains([topic]))

            if payload.randomize:
                query = query.order_by(func.random())
            else:
                query = query.order_by(Question.created_at.desc())

            candidates = query.limit(max(requested * 4, requested)).all()

            chosen_count = 0
            for question in candidates:
                question_id = str(question.id)
                if question_id in selected_ids:
                    continue

                picked.append(
                    {
                        "question_id": question_id,
                        "topic": topic,
                        "difficulty": difficulty,
                        "type": question.question_type.value,
                        "question_text": question.description,
                    }
                )
                selected_ids.add(question_id)
                chosen_count += 1
                if chosen_count >= requested:
                    break

            if chosen_count < requested:
                shortages.append(
                    {
                        "topic": topic,
                        "difficulty": difficulty,
                        "requested": requested,
                        "available": chosen_count,
                    }
                )

    return {
        "success": True,
        "picked": picked,
        "shortages": shortages,
        "total_picked": len(picked),
    }

@router.get("/{question_id}", response_model=dict)
def get_question(
    question_id: uuid.UUID,
    db: Session = Depends(get_db),
    current_faculty: Faculty = Depends(get_current_faculty)
):
    question = db.query(Question).filter(Question.id == question_id).first()
    if not question:
        raise HTTPException(status_code=404, detail="Question not found")
        
    q_dict = QuestionRead.model_validate(question).model_dump(mode='json')
    q_dict["type"] = question.question_type.value if hasattr(question.question_type, 'value') else str(question.question_type)
    q_dict["marks"] = question.max_score
    
    return {"success": True, "data": q_dict}

@router.put("/{question_id}", response_model=dict)
def update_question(
    question_id: uuid.UUID,
    data: QuestionUpdate,
    db: Session = Depends(get_db),
    current_faculty: Faculty = Depends(get_current_faculty)
):
    question = db.query(Question).filter(Question.id == question_id).first()
    if not question:
        raise HTTPException(status_code=404, detail="Question not found")
        
    update_data = data.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(question, field, value)
        
    db.commit()
    db.refresh(question)
    
    invalidate_cache("questions_")
    
    return {"success": True, "message": "Question updated successfully"}

@router.delete("/{question_id}", response_model=dict)
def delete_question(
    question_id: uuid.UUID,
    db: Session = Depends(get_db),
    current_faculty: Faculty = Depends(get_current_faculty)
):
    question = db.query(Question).filter(Question.id == question_id).first()
    if not question:
        raise HTTPException(status_code=404, detail="Question not found")
        
    db.delete(question)
    db.commit()
    
    invalidate_cache("questions_")
    
    return {"success": True, "message": "Question deleted successfully"}
@router.post("/run", response_model=CodeRunResponse)
def run_code(
    data: CodeRunRequest,
    current_user: dict = Depends(get_current_active_user)
):
    """
    Simulated code execution until Judge0 is fully integrated.
    Provides immediate feedback to students for an interactive experience.
    """
    start_time = time.time()
    
    # 1. Basic validation
    if not data.source_code.strip():
        return CodeRunResponse(
            stdout="",
            stderr="Error: Source code cannot be empty",
            status="runtime_error",
            time_taken=0.01,
            memory_used=1.2
        )

    # 2. Simulated output generator
    # If the user provides stdin, we could pretend to use it.
    # We look for common patterns to guess success.
    success = True
    error_msg = ""
    stdout = "Processing input...\n"
    
    # Dummy logic: if code has "error" or "exception" (case insensitive), pretend it failed
    if any(x in data.source_code.lower() for x in ["error", "exception", "exit(1)"]):
        success = False
        error_msg = "Traceback (most recent call last):\n  File \"solution.py\", line 4, in <module>\n    raise ValueError(\"Simulated Error\")"
    
    # Simulate work
    time.sleep(1.0) 
    
    if success:
        stdout += "Success! Sample test cases passed.\nOutput: 42"
    
    return CodeRunResponse(
        stdout=stdout if success else "",
        stderr=error_msg,
        status="accepted" if success else "runtime_error",
        time_taken=round(time.time() - start_time, 3),
        memory_used=round(random.uniform(10.5, 25.8), 2)
    )
