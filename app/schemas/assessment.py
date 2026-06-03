"""
Pydantic schemas for Assessment model.
"""

from datetime import datetime
from typing import Optional, Any
from decimal import Decimal
import uuid

from pydantic import BaseModel, ConfigDict, Field, field_validator, AliasChoices

from app.models.enums import AssessmentType

class AssessmentQuestionAdd(BaseModel):
    """Schema for adding a question to an assessment."""
    question_id: uuid.UUID
    marks: Optional[int] = Field(None, ge=1)
    question_order: Optional[int] = Field(None, ge=1)

class AssessmentBase(BaseModel):
    title: str = Field(..., max_length=500)
    description: str
    type: AssessmentType = Field(alias="type", validation_alias=AliasChoices("type", "assessment_type"))
    duration: int = Field(..., gt=0, alias="duration", validation_alias=AliasChoices("duration", "duration_minutes"))
    date: Optional[str] = None
    time: Optional[str] = None
    registrationDeadline: Optional[str] = None
    maxScore: int = Field(..., ge=0, alias="maxScore", validation_alias=AliasChoices("maxScore", "total_marks"))
    passingScore: Optional[int] = Field(None, ge=0, alias="passingScore", validation_alias=AliasChoices("passingScore", "passing_marks"))
    departments: Optional[list[str]] = Field(None, alias="departments", validation_alias=AliasChoices("departments", "target_branches"))
    batches: Optional[list[str]] = Field(None, alias="batches", validation_alias=AliasChoices("batches", "target_years"))
    shuffleQuestions: bool = False
    showResultsImmediately: bool = False
    minCGPA: Optional[float] = None
    status: str = "draft"
    totalQuestions: Optional[int] = 0
    
    # Direct publish & scheduling fields (alternative to date+time)
    is_published: bool = False
    start_time: Optional[str] = None   # ISO datetime string like "2026-03-14T10:00:00Z"
    end_time: Optional[str] = None     # ISO datetime string
    
    # Proctoring settings
    enable_proctoring: bool = False
    track_tab_switches: bool = False
    tab_switch_limit: int = 3
    instructions: Optional[str] = None
    max_attempts: int = 1

    @field_validator("minCGPA", "passingScore", "totalQuestions", "duration", "maxScore", mode="before")
    @classmethod
    def handle_empty_strings(cls, v):
        if v == "":
            return None
        return v
        
    model_config = ConfigDict(populate_by_name=True)

class AssessmentCreate(AssessmentBase):
    pass

class AssessmentUpdate(BaseModel):
    """Schema for updating an assessment. All fields are optional for partial updates."""
    title: Optional[str] = Field(None, max_length=500)
    description: Optional[str] = None
    type: Optional[AssessmentType] = Field(None, alias="type", validation_alias=AliasChoices("type", "assessment_type"))
    duration: Optional[int] = Field(None, gt=0, alias="duration", validation_alias=AliasChoices("duration", "duration_minutes"))
    date: Optional[str] = None
    time: Optional[str] = None
    registrationDeadline: Optional[str] = None
    maxScore: Optional[int] = Field(None, ge=0, alias="maxScore", validation_alias=AliasChoices("maxScore", "total_marks"))
    passingScore: Optional[int] = Field(None, ge=0, alias="passingScore", validation_alias=AliasChoices("passingScore", "passing_marks"))
    departments: Optional[list[str]] = Field(None, alias="departments", validation_alias=AliasChoices("departments", "target_branches"))
    batches: Optional[list[str]] = Field(None, alias="batches", validation_alias=AliasChoices("batches", "target_years"))
    shuffleQuestions: Optional[bool] = None
    showResultsImmediately: Optional[bool] = None
    minCGPA: Optional[float] = None
    totalQuestions: Optional[int] = None
    is_published: Optional[bool] = None
    start_time: Optional[str] = None
    end_time: Optional[str] = None
    enable_proctoring: Optional[bool] = None
    track_tab_switches: Optional[bool] = None
    tab_switch_limit: Optional[int] = None
    instructions: Optional[str] = None
    max_attempts: Optional[int] = None

    @field_validator("minCGPA", "passingScore", "totalQuestions", "duration", "maxScore", mode="before")
    @classmethod
    def handle_empty_strings(cls, v):
        if v == "":
            return None
        return v

    model_config = ConfigDict(populate_by_name=True)

class AssessmentRead(BaseModel):
    id: uuid.UUID
    title: str
    description: str
    type: str = "" # Mapped manually
    duration: int = Field(0, alias="duration_minutes")
    date: Optional[Any] = None
    time: Optional[Any] = None
    registrationDeadline: Optional[Any] = Field(None, alias="registration_deadline")
    maxScore: int = Field(0, alias="total_marks")
    passingScore: Optional[int] = Field(None, alias="passing_marks")
    departments: Optional[list[str]] = Field(None, alias="target_branches")
    batches: Optional[list[str]] = Field(None, alias="target_years")
    shuffleQuestions: bool = Field(False, alias="shuffle_questions")
    showResultsImmediately: bool = Field(False, alias="show_results_immediately")
    minCGPA: Optional[float] = Field(None, alias="min_cgpa")
    enable_proctoring: bool = False
    track_tab_switches: bool = Field(False, alias="track_tab_switches")
    tab_switch_limit: int = Field(3, alias="tab_switch_limit")
    status: str = "draft"
    totalQuestions: int = Field(0, alias="total_questions")
    
    # Extra aggregated fields requested
    participants: Optional[int] = 0
    avgScore: Optional[float] = 0.0

    slug: Optional[str] = ""
    is_active: bool = True
    total_attempts: int = 0
    created_by: uuid.UUID
    created_at: datetime

    @field_validator("date", "time", "registrationDeadline", mode="before")
    @classmethod
    def format_datetimes(cls, v):
        if isinstance(v, datetime):
            return v.isoformat()
        return v
    
    model_config = ConfigDict(populate_by_name=True, from_attributes=True)

class AssessmentAssigned(BaseModel):
    id: uuid.UUID
    title: str
    type: str = ""
    duration: int = 0
    date: Optional[str] = None
    time: Optional[str] = None
    status: str = "draft"
    totalQuestions: int = 0
    
    # Extra fields for assigned/students
    totalParticipants: Optional[int] = 0
    maxScore: int = 0
    score: Optional[float] = None
    result: Optional[str] = None
    timeTaken: Optional[int] = None
    rank: Optional[int] = None

    model_config = ConfigDict(populate_by_name=True, from_attributes=True)

class AssessmentWithQuestions(AssessmentRead):
    questions: list[dict[str, Any]] = []

    model_config = ConfigDict(from_attributes=True)

class AnswerSubmit(BaseModel):
    question_id: uuid.UUID
    question_type: str
    selected_option: Optional[int] = None
    source_code: Optional[str] = None
    language: Optional[str] = None

class ProctoringEvent(BaseModel):
    event: str
    timestamp: datetime

class AssessmentAttemptSubmitRequest(BaseModel):
    attempt_id: uuid.UUID
    time_taken_minutes: int
    tab_switch_count: int
    answers: list[AnswerSubmit]
    proctoring_events: list[ProctoringEvent] = []
