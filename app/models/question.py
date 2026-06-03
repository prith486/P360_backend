"""
Question model for coding problems.
"""

from typing import Optional, Any, TYPE_CHECKING
from decimal import Decimal

import uuid
from sqlalchemy import (
    String, Integer, Numeric, Boolean, ForeignKey, Text,
    Enum as SQLEnum, Index
)
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import BaseModel
from app.models.enums import DifficultyLevel, QuestionType

if TYPE_CHECKING:
    from app.models.auth_user import AuthUser
    from app.models.assessment_question import AssessmentQuestion
    from app.models.submission import Submission


class Question(BaseModel):
    """Coding question/problem model."""
    
    __tablename__ = "questions"
    
    # Basic information
    title: Mapped[str] = mapped_column(
        String(500),
        nullable=False,
        comment="Question title"
    )
    
    slug: Mapped[str] = mapped_column(
        String(255),
        unique=True,
        nullable=False,
        index=True,
        comment="URL-friendly slug"
    )
    
    difficulty: Mapped[DifficultyLevel] = mapped_column(
        SQLEnum(DifficultyLevel, name="difficulty_level", values_callable=lambda x: [e.value for e in x], create_type=False),
        nullable=False,
        index=True,
        comment="Difficulty level"
    )
    
    question_type: Mapped[QuestionType] = mapped_column(
        SQLEnum(QuestionType, name="question_type", values_callable=lambda x: [e.value for e in x], create_type=False),
        nullable=False,
        default=QuestionType.CODING,
        comment="Type of question"
    )
    
    # Content
    description: Mapped[str] = mapped_column(
        Text,
        nullable=False,
        comment="Problem statement (Markdown supported)"
    )
    
    input_format: Mapped[Optional[str]] = mapped_column(
        Text,
        nullable=True,
        comment="Input format description"
    )
    
    output_format: Mapped[Optional[str]] = mapped_column(
        Text,
        nullable=True,
        comment="Output format description"
    )
    
    constraints: Mapped[Optional[str]] = mapped_column(
        Text,
        nullable=True,
        comment="Problem constraints"
    )
    
    # Test cases (JSONB)
    sample_test_cases: Mapped[Optional[list[dict[str, Any]]]] = mapped_column(
        JSONB,
        default=list,
        nullable=True,
        comment="Sample test cases visible to students"
    )
    
    hidden_test_cases: Mapped[Optional[list[dict[str, Any]]]] = mapped_column(
        JSONB,
        default=list,
        nullable=True,
        comment="Hidden test cases for evaluation"
    )
    
    # Starter code templates (JSONB)
    starter_code: Mapped[Optional[dict[str, str]]] = mapped_column(
        JSONB,
        default=dict,
        nullable=True,
        comment="Starter code templates by language"
    )
    
    solution_code: Mapped[Optional[dict[str, str]]] = mapped_column(
        JSONB,
        default=dict,
        nullable=True,
        comment="Model solution by language"
    )
    
    options: Mapped[Optional[list[dict[str, Any]]]] = mapped_column(
        JSONB,
        default=list,
        nullable=True,
        comment="Options for MCQ questions"
    )
    
    # Hints and explanations
    hints: Mapped[Optional[list[str]]] = mapped_column(
        JSONB,
        default=list,
        nullable=True,
        comment="Hints for solving the problem"
    )
    
    editorial: Mapped[Optional[str]] = mapped_column(
        Text,
        nullable=True,
        comment="Editorial/solution explanation"
    )
    
    # Scoring
    max_score: Mapped[int] = mapped_column(
        Integer,
        default=100,
        nullable=False,
        comment="Maximum score for this question"
    )
    
    time_limit_seconds: Mapped[int] = mapped_column(
        Integer,
        default=2,
        nullable=False,
        comment="Time limit per test case (seconds)"
    )
    
    memory_limit_mb: Mapped[int] = mapped_column(
        Integer,
        default=256,
        nullable=False,
        comment="Memory limit (MB)"
    )
    
    # Metadata
    tags: Mapped[Optional[list[str]]] = mapped_column(
        JSONB,
        default=list,
        nullable=True,
        comment="Topic tags (arrays, dp, graphs, etc.)"
    )
    
    companies: Mapped[Optional[list[str]]] = mapped_column(
        JSONB,
        default=list,
        nullable=True,
        comment="Companies that asked this question"
    )
    
    external_links: Mapped[Optional[dict[str, str]]] = mapped_column(
        JSONB,
        default=dict,
        nullable=True,
        comment="Links to original problem (LeetCode, etc.)"
    )

    source: Mapped[Optional[str]] = mapped_column(
        String(100),
        nullable=True,
        comment="Question source: AI Generated, Manual, Imported"
    )
    
    # Statistics
    total_submissions: Mapped[int] = mapped_column(
        Integer,
        default=0,
        nullable=False,
        comment="Total submissions received"
    )
    
    total_accepted: Mapped[int] = mapped_column(
        Integer,
        default=0,
        nullable=False,
        comment="Total accepted submissions"
    )
    
    acceptance_rate: Mapped[Decimal] = mapped_column(
        Numeric(5, 2),
        default=Decimal("0.0"),
        nullable=False,
        comment="Acceptance rate percentage"
    )
    
    # Publishing
    is_public: Mapped[bool] = mapped_column(
        Boolean,
        default=False,
        nullable=False,
        comment="Publicly visible to all students"
    )
    
    is_active: Mapped[bool] = mapped_column(
        Boolean,
        default=True,
        nullable=False,
        comment="Question is active"
    )
    
    # Creator information
    created_by: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("auth.users.id"),
        nullable=False,
        comment="User ID who created this question"
    )
    
    # Relationships
    creator: Mapped["AuthUser"] = relationship(
        "AuthUser",
        foreign_keys=[created_by]
    )
    
    assessment_mappings: Mapped[list["AssessmentQuestion"]] = relationship(
        "AssessmentQuestion",
        back_populates="question",
        cascade="all, delete-orphan"
    )
    
    submissions: Mapped[list["Submission"]] = relationship(
        "Submission",
        back_populates="question",
        cascade="all, delete-orphan"
    )
    
    # Table arguments (indexes)
    __table_args__ = (
        Index("idx_question_difficulty", "difficulty"),
        Index("idx_question_type", "question_type"),
        Index("idx_question_public_active", "is_public", "is_active"),
        Index("idx_question_tags", "tags", postgresql_using="gin"),
        Index("idx_question_companies", "companies", postgresql_using="gin"),
    )
    
    def __repr__(self) -> str:
        return f"<Question(id={self.id}, title='{self.title[:30]}...', difficulty={self.difficulty.value})>"
    
    def calculate_acceptance_rate(self) -> None:
        """Calculate and update acceptance rate."""
        if self.total_submissions > 0:
            self.acceptance_rate = Decimal(str(
                (self.total_accepted / self.total_submissions) * 100
            )).quantize(Decimal("0.01"))
        else:
            self.acceptance_rate = Decimal("0.0")
