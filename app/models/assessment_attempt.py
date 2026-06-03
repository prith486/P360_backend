"""
Assessment attempt model for tracking student test attempts.
"""

from datetime import datetime
from typing import Optional, Any, TYPE_CHECKING
from decimal import Decimal

import uuid
from sqlalchemy import (
    String, Integer, Numeric, DateTime, ForeignKey, Index, Text,
    Boolean, UniqueConstraint
)
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import BaseModel

if TYPE_CHECKING:
    from app.models.student import Student
    from app.models.assessment import Assessment
    from app.models.submission import Submission


class AssessmentAttempt(BaseModel):
    """Tracks a student's attempt at an assessment."""
    
    __tablename__ = "assessment_attempts"
    
    # Foreign keys
    student_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("students.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
        comment="Student making the attempt"
    )
    
    assessment_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("assessments.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
        comment="Assessment being attempted"
    )
    
    # Attempt tracking
    attempt_number: Mapped[int] = mapped_column(
        Integer,
        default=1,
        nullable=False,
        comment="Attempt number for this student"
    )
    
    # Timing
    started_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        default=datetime.utcnow,
        comment="When attempt started"
    )
    
    submitted_at: Mapped[Optional[datetime]] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
        comment="When attempt was submitted"
    )
    
    time_taken_minutes: Mapped[Optional[int]] = mapped_column(
        Integer,
        nullable=True,
        comment="Total time taken in minutes"
    )
    
    # Scoring
    total_score: Mapped[Decimal] = mapped_column(
        Numeric(7, 2),
        default=Decimal("0.0"),
        nullable=False,
        comment="Total score achieved"
    )
    
    max_score: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
        comment="Maximum possible score"
    )
    
    percentage: Mapped[Optional[Decimal]] = mapped_column(
        Numeric(5, 2),
        nullable=True,
        comment="Score percentage"
    )
    
    is_passed: Mapped[Optional[bool]] = mapped_column(
        Boolean,
        nullable=True,
        comment="Whether student passed"
    )
    
    # Progress tracking
    questions_attempted: Mapped[int] = mapped_column(
        Integer,
        default=0,
        nullable=False,
        comment="Number of questions attempted"
    )
    
    questions_correct: Mapped[int] = mapped_column(
        Integer,
        default=0,
        nullable=False,
        comment="Number of questions fully correct"
    )
    
    # Detailed results (JSONB)
    question_scores: Mapped[Optional[dict[str, Any]]] = mapped_column(
        JSONB,
        default=dict,
        nullable=True,
        comment="Score breakdown by question ID"
    )
    
    # Proctoring data (JSONB)
    proctoring_events: Mapped[Optional[list[dict[str, Any]]]] = mapped_column(
        JSONB,
        default=list,
        nullable=True,
        comment="Proctoring events (tab switches, warnings, etc.)"
    )
    
    tab_switch_count: Mapped[int] = mapped_column(
        Integer,
        default=0,
        nullable=False,
        comment="Number of tab switches detected"
    )

    violation_flag: Mapped[bool] = mapped_column(
        Boolean,
        default=False,
        nullable=False,
        comment="Flagged for proctoring violation"
    )

    violation_reason: Mapped[Optional[str]] = mapped_column(
        String(255),
        nullable=True,
        comment="Reason for violation flag"
    )
    
    # Status
    is_submitted: Mapped[bool] = mapped_column(
        Boolean,
        default=False,
        nullable=False,
        comment="Whether attempt has been submitted"
    )
    
    is_graded: Mapped[bool] = mapped_column(
        Boolean,
        default=False,
        nullable=False,
        comment="Whether attempt has been graded"
    )
    
    # Ranking
    rank: Mapped[Optional[int]] = mapped_column(
        Integer,
        nullable=True,
        comment="Rank among all attempts"
    )
    
    # Notes
    feedback: Mapped[Optional[str]] = mapped_column(
        Text,
        nullable=True,
        comment="Faculty feedback on attempt"
    )
    
    # Relationships
    student: Mapped["Student"] = relationship(
        "Student",
        back_populates="assessment_attempts"
    )
    
    assessment: Mapped["Assessment"] = relationship(
        "Assessment",
        back_populates="attempts"
    )
    
    submissions: Mapped[list["Submission"]] = relationship(
        "Submission",
        back_populates="assessment_attempt",
        cascade="all, delete-orphan"
    )
    
    # Table arguments
    __table_args__ = (
        UniqueConstraint("student_id", "assessment_id", "attempt_number", name="uq_student_assessment_attempt"),
        Index("idx_attempt_student_assessment", "student_id", "assessment_id"),
        Index("idx_attempt_submitted", "is_submitted"),
        Index("idx_attempt_score", "total_score"),
    )
    
    def __repr__(self) -> str:
        return f"<AssessmentAttempt(id={self.id}, student_id={self.student_id}, assessment_id={self.assessment_id}, attempt={self.attempt_number}, score={self.total_score})>"
    
    def calculate_percentage(self) -> None:
        """Calculate score percentage."""
        if self.max_score > 0:
            self.percentage = Decimal(str(
                (float(self.total_score) / self.max_score) * 100
            )).quantize(Decimal("0.01"))
        else:
            self.percentage = Decimal("0.0")
    
    def calculate_time_taken(self) -> None:
        """Calculate time taken if submitted."""
        if self.submitted_at and self.started_at:
            delta = self.submitted_at - self.started_at
            self.time_taken_minutes = int(delta.total_seconds() / 60)
    
    def add_proctoring_event(self, event_type: str, details: dict[str, Any]) -> None:
        """Add a proctoring event."""
        if self.proctoring_events is None:
            self.proctoring_events = []
        self.proctoring_events.append({
            "type": event_type,
            "timestamp": datetime.utcnow().isoformat(),
            "details": details
        })
        if event_type == "tab_switch":
            self.tab_switch_count += 1
