"""Schemas for AI generation, smart picker, and generated assessment flows."""

from typing import Any, Literal, Optional
from pydantic import BaseModel, Field


class GenerateQuestionsRequest(BaseModel):
    topic: str = Field(..., min_length=1)
    difficulty: str | list[str]
    question_type: Literal["coding", "mcq", "mixed"]
    count: int = Field(..., ge=1, le=100)
    role_tags: Optional[list[str]] = None
    company_tags: Optional[list[str]] = None
    additional_instructions: Optional[str] = None


class GenerateQuestionsSaveRequest(BaseModel):
    questions: list[dict[str, Any]] = Field(default_factory=list)


class TopicDistributionSlot(BaseModel):
    topic: str
    easy: int = Field(0, ge=0)
    medium: int = Field(0, ge=0)
    hard: int = Field(0, ge=0)
    expert: int = Field(0, ge=0)


class GenerateTestRequest(BaseModel):
    title: str
    topic_distribution: list[TopicDistributionSlot] = Field(default_factory=list)
    question_type_mix: Literal["mcq", "coding", "mixed"] = "mixed"
    target_cgpa_min: Optional[float] = None
    duration_minutes: int = Field(..., ge=1)
    existing_question_ids: list[str] = Field(default_factory=list)


class AssessmentMetaPayload(BaseModel):
    title: str
    start_time: Optional[str] = None
    end_time: Optional[str] = None
    duration: int = Field(..., ge=1)
    branch: Optional[list[str]] = None
    year: Optional[list[str]] = None
    proctoring_config: Optional[dict[str, Any]] = None
    description: Optional[str] = "AI Generated Assessment"
    passing_score: Optional[int] = Field(default=0, ge=0)


class GenerateAssessmentConfirmRequest(BaseModel):
    assessment_meta: AssessmentMetaPayload
    selected_bank_question_ids: list[str] = Field(default_factory=list)
    new_questions_to_save: list[dict[str, Any]] = Field(default_factory=list)
    question_order: list[str] = Field(default_factory=list)


class SmartPickerCriterion(BaseModel):
    topic: str
    easy: int = Field(0, ge=0)
    medium: int = Field(0, ge=0)
    hard: int = Field(0, ge=0)
    expert: int = Field(0, ge=0)
    types: list[Literal["mcq", "coding", "subjective"]] = Field(default_factory=lambda: ["mcq", "coding"])


class SmartPickerRequest(BaseModel):
    criteria: list[SmartPickerCriterion] = Field(default_factory=list)
    exclude_question_ids: list[str] = Field(default_factory=list)
    randomize: bool = True
