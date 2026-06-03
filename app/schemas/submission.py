"""
Pydantic schemas for Submission model.
"""

from datetime import datetime
from typing import Optional, Any
from decimal import Decimal

from pydantic import BaseModel, Field, ConfigDict

from app.models.enums import SubmissionStatus, ProgrammingLanguage


class SubmissionCreate(BaseModel):
    """Schema for creating submission."""
    question_id: int
    language: ProgrammingLanguage
    source_code: str = Field(..., min_length=1)
    assessment_attempt_id: Optional[int] = None


class SubmissionRead(BaseModel):
    """Schema for submission response."""
    id: int
    student_id: int
    question_id: int
    language: ProgrammingLanguage
    status: SubmissionStatus
    execution_time_ms: Optional[int] = None
    memory_used_kb: Optional[int] = None
    total_test_cases: int
    passed_test_cases: int
    score: Decimal
    max_score: int
    submitted_at: datetime
    evaluated_at: Optional[datetime] = None
    
    model_config = ConfigDict(from_attributes=True)


class SubmissionDetailed(SubmissionRead):
    """Detailed schema including code and results."""
    source_code: str
    stdout: Optional[str] = None
    stderr: Optional[str] = None
    compile_output: Optional[str] = None
    test_case_results: Optional[list[dict[str, Any]]] = None
    
    model_config = ConfigDict(from_attributes=True)
