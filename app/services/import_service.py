"""Bulk question import parsing and validation service."""

from __future__ import annotations

from io import BytesIO
import csv
import re
from typing import Any, Optional

import openpyxl
import pdfplumber


EXPECTED_COLUMNS = {
    "question_text",
    "type",
    "difficulty",
    "tags",
    "option_a",
    "option_b",
    "option_c",
    "option_d",
    "correct_option",
    "explanation",
}

VALID_TYPES = {"mcq", "coding"}
VALID_DIFFICULTIES = {"easy", "medium", "hard", "expert"}


def _normalize_header(value: Any) -> str:
    if value is None:
        return ""
    return str(value).strip().lower().replace(" ", "_")


def _clean_text(value: Any) -> Optional[str]:
    if value is None:
        return None
    text = str(value).strip()
    return text or None


def _parse_tags(value: Any) -> list[str]:
    if value is None:
        return []
    if isinstance(value, list):
        return [str(v).strip() for v in value if str(v).strip()]
    if isinstance(value, str):
        return [chunk.strip() for chunk in value.split(",") if chunk.strip()]
    return []


def _normalize_row(row_data: dict[str, Any], row_number: int) -> dict[str, Any]:
    item = {
        "_row": row_number,
        "question_text": _clean_text(row_data.get("question_text")),
        "type": (_clean_text(row_data.get("type")) or "").lower() or None,
        "difficulty": (_clean_text(row_data.get("difficulty")) or "").lower() or None,
        "tags": _parse_tags(row_data.get("tags")),
        "option_a": _clean_text(row_data.get("option_a")),
        "option_b": _clean_text(row_data.get("option_b")),
        "option_c": _clean_text(row_data.get("option_c")),
        "option_d": _clean_text(row_data.get("option_d")),
        "correct_option": (_clean_text(row_data.get("correct_option")) or "").upper() or None,
        "explanation": _clean_text(row_data.get("explanation")),
    }
    return item


def parse_excel(file_bytes: bytes) -> list[dict[str, Any]]:
    """Parse .xlsx into normalized row dictionaries."""

    workbook = openpyxl.load_workbook(BytesIO(file_bytes), data_only=True)
    sheet = workbook.active

    rows = list(sheet.iter_rows(values_only=True))
    if not rows:
        return []

    headers = [_normalize_header(h) for h in rows[0]]
    normalized: list[dict[str, Any]] = []

    for idx, raw_row in enumerate(rows[1:], start=2):
        if not any(cell is not None and str(cell).strip() for cell in raw_row):
            continue

        mapped = {}
        for col_idx, header in enumerate(headers):
            if header in EXPECTED_COLUMNS and col_idx < len(raw_row):
                mapped[header] = raw_row[col_idx]

        normalized.append(_normalize_row(mapped, idx))

    return normalized


def parse_csv(file_bytes: bytes) -> list[dict[str, Any]]:
    """Parse .csv into normalized row dictionaries."""

    decoded = file_bytes.decode("utf-8-sig", errors="ignore")
    reader = csv.DictReader(decoded.splitlines())

    normalized: list[dict[str, Any]] = []
    for idx, raw_row in enumerate(reader, start=2):
        mapped: dict[str, Any] = {}
        for key, value in raw_row.items():
            header = _normalize_header(key)
            if header in EXPECTED_COLUMNS:
                mapped[header] = value
        normalized.append(_normalize_row(mapped, idx))

    return normalized


def parse_pdf(file_bytes: bytes) -> list[dict[str, Any]]:
    """Best-effort parse for question blocks in PDF text."""

    text_parts: list[str] = []
    with pdfplumber.open(BytesIO(file_bytes)) as pdf:
        for page in pdf.pages:
            page_text = page.extract_text() or ""
            if page_text.strip():
                text_parts.append(page_text)

    full_text = "\n".join(text_parts).strip()
    if not full_text:
        return []

    # Match numbered patterns: "1. ...", "Q1.", "Q2:" etc.
    pattern = re.compile(r"(?:^|\n)\s*(?:Q\s*\d+|\d+)\s*[\).:\-]\s*", re.IGNORECASE)
    matches = list(pattern.finditer(full_text))

    blocks: list[str] = []
    if matches:
        for i, match in enumerate(matches):
            start = match.end()
            end = matches[i + 1].start() if i + 1 < len(matches) else len(full_text)
            candidate = full_text[start:end].strip()
            if candidate:
                blocks.append(candidate)
    else:
        # Fallback to paragraph split if numbering is absent.
        for part in re.split(r"\n\s*\n+", full_text):
            cleaned = part.strip()
            if cleaned:
                blocks.append(cleaned)

    parsed: list[dict[str, Any]] = []
    for idx, block in enumerate(blocks, start=1):
        parsed.append(
            {
                "_row": idx,
                "question_text": block,
                "type": None,
                "difficulty": None,
                "tags": [],
                "needs_review": True,
            }
        )

    return parsed


def validate_and_map(parsed_rows: list[dict[str, Any]]) -> tuple[list[dict[str, Any]], list[dict[str, Any]]]:
    """Split parsed rows into valid and invalid payloads for question creation."""

    valid_list: list[dict[str, Any]] = []
    invalid_list: list[dict[str, Any]] = []

    for idx, row in enumerate(parsed_rows):
        row_num = row.get("_row", idx + 1)
        question_text = _clean_text(row.get("question_text"))
        q_type = (_clean_text(row.get("type")) or "").lower() or None
        difficulty = (_clean_text(row.get("difficulty")) or "").lower() or None

        if not question_text:
            invalid_list.append({"row": row_num, "reason": "question_text is required", "data": row})
            continue

        if q_type not in VALID_TYPES:
            invalid_list.append({"row": row_num, "reason": "type must be mcq or coding", "data": row})
            continue

        if difficulty not in VALID_DIFFICULTIES:
            invalid_list.append(
                {
                    "row": row_num,
                    "reason": "difficulty must be easy, medium, hard, or expert",
                    "data": row,
                }
            )
            continue

        mapped = {
            "question_text": question_text,
            "type": q_type,
            "difficulty": difficulty,
            "tags": _parse_tags(row.get("tags")),
            "explanation": _clean_text(row.get("explanation")),
            "needs_review": bool(row.get("needs_review", False)),
        }

        if q_type == "mcq":
            option_a = _clean_text(row.get("option_a"))
            option_b = _clean_text(row.get("option_b"))
            option_c = _clean_text(row.get("option_c"))
            option_d = _clean_text(row.get("option_d"))
            correct_option = (_clean_text(row.get("correct_option")) or "").upper() or None

            if not all([option_a, option_b, option_c, option_d]):
                invalid_list.append(
                    {
                        "row": row_num,
                        "reason": "mcq requires option_a, option_b, option_c, and option_d",
                        "data": row,
                    }
                )
                continue

            if correct_option not in {"A", "B", "C", "D"}:
                invalid_list.append(
                    {
                        "row": row_num,
                        "reason": "mcq correct_option must be one of A/B/C/D",
                        "data": row,
                    }
                )
                continue

            mapped["options"] = {
                "A": option_a,
                "B": option_b,
                "C": option_c,
                "D": option_d,
            }
            mapped["correct_option"] = correct_option

        valid_list.append(mapped)

    return valid_list, invalid_list
