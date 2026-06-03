"""Bulk question import endpoints."""

from __future__ import annotations

from datetime import datetime
import uuid
from typing import Any

from fastapi import APIRouter, BackgroundTasks, Depends, File, HTTPException, UploadFile
from sqlalchemy.orm import Session

from app.api.deps import get_current_faculty
from app.core.cache import invalidate_cache
from app.core.database import SessionLocal, get_db
from app.models.enums import DifficultyLevel, QuestionType
from app.models.faculty import Faculty
from app.models.question import Question
from app.models.question_import_job import (
    ImportFileType,
    ImportJobStatus,
    QuestionImportJob,
)
from app.schemas.import_job import ImportConfirmRequest
from app.services.import_service import (
    parse_csv,
    parse_excel,
    parse_pdf,
    validate_and_map,
)

router = APIRouter()


def _detect_file_type(filename: str) -> ImportFileType:
    lowered = filename.lower()
    if lowered.endswith(".xlsx"):
        return ImportFileType.XLSX
    if lowered.endswith(".csv"):
        return ImportFileType.CSV
    if lowered.endswith(".pdf"):
        return ImportFileType.PDF
    raise HTTPException(status_code=400, detail="Unsupported file type. Use .xlsx, .csv, or .pdf")


def _parse_by_file_type(file_bytes: bytes, file_type: ImportFileType) -> list[dict[str, Any]]:
    if file_type == ImportFileType.XLSX:
        return parse_excel(file_bytes)
    if file_type == ImportFileType.CSV:
        return parse_csv(file_bytes)
    if file_type == ImportFileType.PDF:
        return parse_pdf(file_bytes)
    return []


def _make_slug(seed_text: str) -> str:
    slug_uuid = str(uuid.uuid4())[:8]
    cleaned = "-".join(seed_text.lower().strip().split())
    cleaned = cleaned[:80] if cleaned else "question"
    return f"{cleaned}-{slug_uuid}"


def _build_question_payload(preview_row: dict[str, Any], faculty_user_id: uuid.UUID) -> dict[str, Any]:
    question_text = str(preview_row.get("question_text", "")).strip()
    q_type = str(preview_row.get("type", "")).lower().strip()
    difficulty = str(preview_row.get("difficulty", "")).lower().strip()
    tags = preview_row.get("tags") or []
    explanation = preview_row.get("explanation")

    payload: dict[str, Any] = {
        "title": question_text[:120] if len(question_text) > 120 else question_text,
        "slug": _make_slug(question_text),
        "difficulty": DifficultyLevel(difficulty),
        "question_type": QuestionType(q_type),
        "description": question_text,
        "tags": tags,
        "editorial": explanation,
        "created_by": faculty_user_id,
        "total_submissions": 0,
        "total_accepted": 0,
        "acceptance_rate": 0.0,
        "is_active": True,
        "source": "Imported",
    }

    if q_type == "mcq":
        options_map = preview_row.get("options", {})
        correct_option = str(preview_row.get("correct_option", "")).strip().upper()
        labels = ["A", "B", "C", "D"]
        formatted_options = []
        correct_index = None
        for index, label in enumerate(labels, start=1):
            opt_text = options_map.get(label)
            formatted_options.append(
                {
                    "id": index,
                    "label": label,
                    "text": opt_text,
                    "is_correct": label == correct_option,
                }
            )
            if label == correct_option:
                correct_index = index

        payload["options"] = formatted_options
        payload["solution_code"] = {"correct_option": correct_index}

    return payload


def _process_import_job(job_id: uuid.UUID, file_bytes: bytes, file_type: ImportFileType) -> None:
    db = SessionLocal()
    try:
        job = db.query(QuestionImportJob).filter(QuestionImportJob.id == job_id).first()
        if not job:
            return

        job.status = ImportJobStatus.PROCESSING
        db.commit()

        parsed_rows = _parse_by_file_type(file_bytes, file_type)
        valid_list, invalid_list = validate_and_map(parsed_rows)

        invalid_by_row = {int(item.get("row", -1)): item.get("reason", "Invalid row") for item in invalid_list}
        preview_rows: list[dict[str, Any]] = []
        for row in parsed_rows:
            row_num = int(row.get("_row", 0))
            preview = dict(row)
            if row_num in invalid_by_row:
                preview["is_valid"] = False
                preview["validation_error"] = invalid_by_row[row_num]
            else:
                preview["is_valid"] = True
            preview_rows.append(preview)

        job.total_rows = len(parsed_rows)
        job.failed_rows = invalid_list
        job.parsed_preview = preview_rows
        job.status = ImportJobStatus.AWAITING_REVIEW
        job.updated_at = datetime.utcnow()

        db.commit()
    except Exception as exc:
        db.rollback()
        job = db.query(QuestionImportJob).filter(QuestionImportJob.id == job_id).first()
        if job:
            job.status = ImportJobStatus.FAILED
            job.failed_rows = [{"row": None, "reason": str(exc)}]
            job.updated_at = datetime.utcnow()
            db.commit()
    finally:
        db.close()


@router.post("/questions", response_model=dict)
async def upload_questions_file(
    background_tasks: BackgroundTasks,
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
    current_faculty: Faculty = Depends(get_current_faculty),
):
    if not file.filename:
        raise HTTPException(status_code=400, detail="Filename is required")

    file_type = _detect_file_type(file.filename)
    file_bytes = await file.read()
    if not file_bytes:
        raise HTTPException(status_code=400, detail="Uploaded file is empty")

    job = QuestionImportJob(
        id=uuid.uuid4(),
        faculty_id=current_faculty.user_id,
        file_type=file_type,
        original_filename=file.filename,
        status=ImportJobStatus.PROCESSING,
        failed_rows=[],
        parsed_preview=[],
        imported_count=0,
    )

    db.add(job)
    db.commit()
    db.refresh(job)

    background_tasks.add_task(_process_import_job, job.id, file_bytes, file_type)

    return {"job_id": str(job.id), "status": "processing"}


@router.get("/questions/history", response_model=dict)
def get_import_history(
    db: Session = Depends(get_db),
    current_faculty: Faculty = Depends(get_current_faculty),
):
    jobs = (
        db.query(QuestionImportJob)
        .filter(QuestionImportJob.faculty_id == current_faculty.user_id)
        .order_by(QuestionImportJob.created_at.desc())
        .all()
    )

    data = [
        {
            "id": str(job.id),
            "file_type": job.file_type.value if hasattr(job.file_type, "value") else str(job.file_type),
            "original_filename": job.original_filename,
            "status": job.status.value if hasattr(job.status, "value") else str(job.status),
            "total_rows": job.total_rows,
            "imported_count": job.imported_count,
            "created_at": job.created_at.isoformat() if job.created_at else None,
        }
        for job in jobs
    ]

    return {"success": True, "data": data}


@router.get("/questions/{job_id}", response_model=dict)
def get_import_job_status(
    job_id: uuid.UUID,
    db: Session = Depends(get_db),
    current_faculty: Faculty = Depends(get_current_faculty),
):
    job = (
        db.query(QuestionImportJob)
        .filter(
            QuestionImportJob.id == job_id,
            QuestionImportJob.faculty_id == current_faculty.user_id,
        )
        .first()
    )

    if not job:
        raise HTTPException(status_code=404, detail="Import job not found")

    return {
        "success": True,
        "data": {
            "id": str(job.id),
            "file_type": job.file_type.value if hasattr(job.file_type, "value") else str(job.file_type),
            "original_filename": job.original_filename,
            "status": job.status.value if hasattr(job.status, "value") else str(job.status),
            "total_rows": job.total_rows,
            "imported_count": job.imported_count,
            "failed_rows": job.failed_rows or [],
            "parsed_preview": job.parsed_preview or [],
            "created_at": job.created_at.isoformat() if job.created_at else None,
            "updated_at": job.updated_at.isoformat() if job.updated_at else None,
        },
    }


@router.post("/questions/{job_id}/confirm", response_model=dict)
def confirm_import_job(
    job_id: uuid.UUID,
    payload: ImportConfirmRequest,
    db: Session = Depends(get_db),
    current_faculty: Faculty = Depends(get_current_faculty),
):
    job = (
        db.query(QuestionImportJob)
        .filter(
            QuestionImportJob.id == job_id,
            QuestionImportJob.faculty_id == current_faculty.user_id,
        )
        .first()
    )

    if not job:
        raise HTTPException(status_code=404, detail="Import job not found")

    if job.status not in {ImportJobStatus.AWAITING_REVIEW, ImportJobStatus.PROCESSING}:
        raise HTTPException(status_code=400, detail="Import job is not ready for confirmation")

    preview_rows = job.parsed_preview or []
    if not preview_rows:
        raise HTTPException(status_code=400, detail="No parsed preview available for this job")

    approved_rows: list[dict[str, Any]] = []
    invalid_selection: list[dict[str, Any]] = []

    for idx in payload.approved_indices:
        if idx < 0 or idx >= len(preview_rows):
            invalid_selection.append({"row": idx, "reason": "Approved index out of range"})
            continue
        approved_rows.append(preview_rows[idx])

    valid_rows, invalid_rows = validate_and_map(approved_rows)
    invalid_rows.extend(invalid_selection)

    created_question_ids: list[str] = []
    for row in valid_rows:
        try:
            question_payload = _build_question_payload(row, current_faculty.user_id)
            question = Question(**question_payload)
            db.add(question)
            db.flush()
            created_question_ids.append(str(question.id))
        except Exception as exc:
            invalid_rows.append({"row": row.get("_row"), "reason": str(exc), "data": row})

    job.imported_count = len(created_question_ids)
    job.failed_rows = invalid_rows
    job.status = ImportJobStatus.COMPLETED
    job.updated_at = datetime.utcnow()

    db.commit()

    if created_question_ids:
        invalidate_cache("questions_")

    return {
        "imported_count": len(created_question_ids),
        "failed_rows": invalid_rows,
        "question_ids": created_question_ids,
    }
