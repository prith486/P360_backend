"""
Pydantic schemas for Question model.
"""

from datetime import datetime
from typing import Optional, Any
from decimal import Decimal
import uuid

from pydantic import BaseModel, Field, ConfigDict

from app.models.enums import DifficultyLevel, QuestionType


class QuestionBase(BaseModel):
    """Base schema with common question fields."""
    title: str = Field(..., min_length=1, max_length=500)
    slug: Optional[str] = Field(None, min_length=3, max_length=255)
    difficulty: DifficultyLevel
    question_type: QuestionType = QuestionType.CODING
    description: str = Field(..., min_length=20)


class QuestionCreate(QuestionBase):
    """Schema for creating question."""
    input_format: Optional[str] = None
    output_format: Optional[str] = None
    constraints: Optional[str] = None
    sample_test_cases: Optional[list[dict[str, Any]]] = None
    hidden_test_cases: Optional[list[dict[str, Any]]] = None
    starter_code: Optional[dict[str, str]] = None
    options: Optional[list[dict[str, Any]]] = None
    hints: Optional[list[str]] = None
    tags: Optional[list[str]] = None
    companies: Optional[list[str]] = None
    source: Optional[str] = Field(None, max_length=100)
    max_score: int = Field(100, ge=1)
    time_limit_seconds: int = Field(2, ge=1, le=30)
    memory_limit_mb: int = Field(256, ge=16, le=1024)
    is_public: bool = False


class QuestionUpdate(BaseModel):
    """Schema for updating question."""
    title: Optional[str] = Field(None, min_length=1, max_length=500)
    description: Optional[str] = None
    difficulty: Optional[DifficultyLevel] = None
    sample_test_cases: Optional[list[dict[str, Any]]] = None
    hidden_test_cases: Optional[list[dict[str, Any]]] = None
    hints: Optional[list[str]] = None
    tags: Optional[list[str]] = None
    source: Optional[str] = Field(None, max_length=100)
    is_public: Optional[bool] = None
    is_active: Optional[bool] = None


class QuestionRead(QuestionBase):
    """Schema for question response."""
    id: uuid.UUID
    sample_test_cases: Optional[list[dict[str, Any]]] = None
    starter_code: Optional[dict[str, str]] = None
    options: Optional[list[dict[str, Any]]] = None
    hints: Optional[list[str]] = None
    tags: Optional[list[str]] = None
    companies: Optional[list[str]] = None
    source: Optional[str] = None
    max_score: int
    time_limit_seconds: int
    memory_limit_mb: int
    total_submissions: int
    total_accepted: int
    acceptance_rate: Decimal
    is_public: bool
    created_at: datetime
    
    model_config = ConfigDict(from_attributes=True)


class QuestionDetailed(QuestionRead):
    """Detailed schema including test cases and editorial."""
    input_format: Optional[str] = None
    output_format: Optional[str] = None
    constraints: Optional[str] = None
    hidden_test_cases: Optional[list[dict[str, Any]]] = None  # Only for faculty/admin
    solution_code: Optional[dict[str, str]] = None  # Only for faculty/admin
    editorial: Optional[str] = None
    external_links: Optional[dict[str, str]] = None
    created_by: uuid.UUID
    
    model_config = ConfigDict(from_attributes=True)


class CodeRunRequest(BaseModel):
    """Schema for code execution request."""
    source_code: str
    language: str
    question_id: Optional[Any] = None
    stdin: Optional[str] = None


class CodeRunResponse(BaseModel):
    """Schema for code execution response."""
    stdout: str
    stderr: str
    status: str
    time_taken: float
    memory_used: float
