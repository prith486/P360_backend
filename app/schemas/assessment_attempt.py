"""
Pydantic schemas for AssessmentAttempt model.
"""

from datetime import datetime
from typing import Optional, Any, List
from decimal import Decimal
import uuid

from pydantic import BaseModel, ConfigDict, Field

from app.schemas.submission import SubmissionRead

class AttemptStartRequest(BaseModel):
    """Schema for starting an attempt if payload is needed (though it can be empty)."""
    pass

class QuestionAnswer(BaseModel):
    """Schema for individual answers in a submission."""
    question_id: str
    question_type: Optional[str] = None
    selected_option: Optional[Any] = None
    source_code: Optional[str] = None
    language: Optional[str] = None

class ProctoringEvent(BaseModel):
    """Schema for proctoring events."""
    event: str
    timestamp: datetime

class AttemptSubmitRequest(BaseModel):
    """Schema for submitting an assessment."""
    attempt_id: str
    time_taken_minutes: Optional[int] = None
    tab_switch_count: Optional[int] = 0
    answers: Optional[List[QuestionAnswer]] = []
    proctoring_events: Optional[List[Any]] = []

class AssessmentAttemptRead(BaseModel):
    """Schema for returning an assessment attempt."""
    id: uuid.UUID
    student_id: uuid.UUID
    assessment_id: uuid.UUID
    attempt_number: int
    started_at: datetime
    submitted_at: Optional[datetime] = None
    time_taken_minutes: Optional[int] = None
    total_score: Decimal
    max_score: int
    percentage: Optional[Decimal] = None
    is_passed: Optional[bool] = None
    questions_attempted: int
    questions_correct: int
    is_submitted: bool
    is_graded: bool
    rank: Optional[int] = None

    model_config = ConfigDict(from_attributes=True)

class AssessmentAttemptDetailed(AssessmentAttemptRead):
    """Schema for returning a detailed assessment attempt."""
    question_scores: Optional[dict[str, Any]] = None
    proctoring_events: Optional[list[dict[str, Any]]] = None
    tab_switch_count: int
    feedback: Optional[str] = None
    submissions: list[SubmissionRead] = []

    model_config = ConfigDict(from_attributes=True)

class FacultyAttemptRead(BaseModel):
    """Schema for faculty listing all attempts."""
    attempt_id: uuid.UUID
    student_id: uuid.UUID
    student_name: str
    roll_number: str
    attempt_number: int
    started_at: datetime
    submitted_at: Optional[datetime] = None
    time_taken_minutes: Optional[int] = None
    total_score: Decimal
    max_score: int
    percentage: Optional[Decimal] = None
    is_passed: Optional[bool] = None
    tab_switch_count: int
    is_submitted: bool
    is_graded: bool
