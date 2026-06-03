"""
Submission model for code execution results.
"""

from datetime import datetime
from typing import Optional, Any, TYPE_CHECKING
from decimal import Decimal

import uuid
from sqlalchemy import (
    String, Integer, Numeric, Boolean, DateTime, ForeignKey, Text,
    Enum as SQLEnum, Index
)
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import BaseModel
from app.models.enums import SubmissionStatus, ProgrammingLanguage

if TYPE_CHECKING:
    from app.models.student import Student
    from app.models.question import Question
    from app.models.assessment_attempt import AssessmentAttempt


class Submission(BaseModel):
    """Code submission model."""
    
    __tablename__ = "submissions"
    
    # Foreign keys
    student_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("students.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
        comment="Student who submitted"
    )
    
    question_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("questions.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
        comment="Question being answered"
    )
    
    assessment_attempt_id: Mapped[Optional[uuid.UUID]] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("assessment_attempts.id", ondelete="SET NULL"),
        nullable=True,
        index=True,
        comment="Assessment attempt (if part of assessment)"
    )
    
    # Code
    language: Mapped[ProgrammingLanguage] = mapped_column(
        SQLEnum(ProgrammingLanguage, name="programming_language", values_callable=lambda x: [e.value for e in x], create_type=False),
        nullable=False,
        comment="Programming language used"
    )
    
    source_code: Mapped[str] = mapped_column(
        Text,
        nullable=False,
        comment="Submitted source code"
    )
    
    # Judge0 integration
    judge0_token: Mapped[Optional[str]] = mapped_column(
        String(100),
        nullable=True,
        comment="Judge0 submission token"
    )
    
    status: Mapped[SubmissionStatus] = mapped_column(
        SQLEnum(SubmissionStatus, name="submission_status", values_callable=lambda x: [e.value for e in x], create_type=False),
        nullable=False,
        default=SubmissionStatus.PENDING,
        index=True,
        comment="Submission status"
    )
    
    # Execution metrics
    execution_time_ms: Mapped[Optional[int]] = mapped_column(
        Integer,
        nullable=True,
        comment="Execution time in milliseconds"
    )
    
    memory_used_kb: Mapped[Optional[int]] = mapped_column(
        Integer,
        nullable=True,
        comment="Memory used in kilobytes"
    )
    
    # Test case results
    total_test_cases: Mapped[int] = mapped_column(
        Integer,
        default=0,
        nullable=False,
        comment="Total number of test cases"
    )
    
    passed_test_cases: Mapped[int] = mapped_column(
        Integer,
        default=0,
        nullable=False,
        comment="Number of passed test cases"
    )
    
    test_case_results: Mapped[Optional[list[dict[str, Any]]]] = mapped_column(
        JSONB,
        default=list,
        nullable=True,
        comment="Detailed results for each test case"
    )
    
    # Compilation output
    stdout: Mapped[Optional[str]] = mapped_column(
        Text,
        nullable=True,
        comment="Standard output"
    )
    
    stderr: Mapped[Optional[str]] = mapped_column(
        Text,
        nullable=True,
        comment="Standard error"
    )
    
    compile_output: Mapped[Optional[str]] = mapped_column(
        Text,
        nullable=True,
        comment="Compilation output/errors"
    )
    
    # Scoring
    score: Mapped[Decimal] = mapped_column(
        Numeric(7, 2),
        default=Decimal("0.0"),
        nullable=False,
        comment="Score awarded"
    )
    
    max_score: Mapped[int] = mapped_column(
        Integer,
        default=100,
        nullable=False,
        comment="Maximum possible score"
    )
    
    partial_credit_enabled: Mapped[bool] = mapped_column(
        Boolean,
        default=True,
        nullable=False,
        comment="Partial credit for passed test cases"
    )
    
    # Timestamps
    submitted_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        default=datetime.utcnow,
        comment="When code was submitted"
    )
    
    evaluated_at: Mapped[Optional[datetime]] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
        comment="When evaluation completed"
    )
    
    # Relationships
    student: Mapped["Student"] = relationship(
        "Student",
        back_populates="submissions"
    )
    
    question: Mapped["Question"] = relationship(
        "Question",
        back_populates="submissions"
    )
    
    assessment_attempt: Mapped[Optional["AssessmentAttempt"]] = relationship(
        "AssessmentAttempt",
        back_populates="submissions"
    )
    
    # Table arguments
    __table_args__ = (
        Index("idx_submission_student_question", "student_id", "question_id"),
        Index("idx_submission_status", "status"),
        Index("idx_submission_submitted_at", "submitted_at"),
    )
    
    def __repr__(self) -> str:
        return f"<Submission(id={self.id}, student_id={self.student_id}, question_id={self.question_id}, status={self.status.value}, score={self.score})>"
    
    def calculate_score(self) -> None:
        """Calculate score based on passed test cases."""
        if self.partial_credit_enabled and self.total_test_cases > 0:
            ratio = self.passed_test_cases / self.total_test_cases
            self.score = Decimal(str(ratio * self.max_score)).quantize(Decimal("0.01"))
        elif self.passed_test_cases == self.total_test_cases:
            self.score = Decimal(str(self.max_score))
        else:
            self.score = Decimal("0.0")
    
    def is_accepted(self) -> bool:
        """Check if submission was fully accepted."""
        return self.status == SubmissionStatus.ACCEPTED
