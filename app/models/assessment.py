"""
Assessment model for tests/contests.
"""

from datetime import datetime
from typing import Optional, Any, TYPE_CHECKING
from decimal import Decimal

import uuid
from sqlalchemy import (
    String, Integer, Numeric, Boolean, DateTime, ForeignKey, Text,
    Enum as SQLEnum, Index
)
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.dialects.postgresql import ARRAY as PG_ARRAY, UUID, JSONB

from app.models.base import BaseModel
from app.models.enums import AssessmentType, BranchType, AcademicYear

if TYPE_CHECKING:
    from app.models.auth_user import AuthUser
    from app.models.assessment_question import AssessmentQuestion
    from app.models.assessment_attempt import AssessmentAttempt


class Assessment(BaseModel):
    """Assessment/test model."""
    
    __tablename__ = "assessments"
    
    # Basic information
    title: Mapped[str] = mapped_column(
        String(500),
        nullable=False,
        comment="Assessment title"
    )
    
    slug: Mapped[str] = mapped_column(
        String(255),
        unique=True,
        nullable=False,
        index=True,
        comment="URL-friendly slug"
    )
    
    description: Mapped[str] = mapped_column(
        Text,
        nullable=False,
        comment="Assessment description"
    )
    
    assessment_type: Mapped[AssessmentType] = mapped_column(
        SQLEnum(AssessmentType, name="assessment_type", values_callable=lambda x: [e.value for e in x], create_type=False),
        nullable=False,
        index=True,
        comment="Type of assessment"
    )
    
    # Timing
    duration_minutes: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
        comment="Total duration in minutes"
    )
    
    start_time: Mapped[Optional[datetime]] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
        comment="Scheduled start time"
    )
    
    end_time: Mapped[Optional[datetime]] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
        comment="Scheduled end time"
    )
    
    # Scoring
    total_marks: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
        comment="Total marks/points"
    )
    
    passing_marks: Mapped[Optional[int]] = mapped_column(
        Integer,
        nullable=True,
        comment="Minimum marks to pass"
    )
    
    # Access control
    is_public: Mapped[bool] = mapped_column(
        Boolean,
        default=False,
        nullable=False,
        comment="Public assessment (visible to all)"
    )
    
    is_published: Mapped[bool] = mapped_column(
        Boolean,
        default=False,
        nullable=False,
        comment="Published and visible to students"
    )
    
    is_active: Mapped[bool] = mapped_column(
        Boolean,
        default=True,
        nullable=False,
        comment="Assessment is active"
    )
    
    status: Mapped[str] = mapped_column(
        String(50),
        default="draft",
        nullable=False,
        comment="Status: draft, scheduled, active, completed"
    )
    
    # Targeting (nullable = open to all)
    target_branches: Mapped[Optional[list[str]]] = mapped_column(
        PG_ARRAY(String),
        nullable=True,
        comment="Target branches (null = all branches)"
    )
    
    target_years: Mapped[Optional[list[str]]] = mapped_column(
        PG_ARRAY(String),
        nullable=True,
        comment="Target academic years (null = all years)"
    )
    
    target_students: Mapped[Optional[list[uuid.UUID]]] = mapped_column(
        PG_ARRAY(UUID(as_uuid=True)),
        nullable=True,
        comment="Specific student IDs (null = all eligible)"
    )
    
    # Attempt settings
    max_attempts: Mapped[int] = mapped_column(
        Integer,
        default=1,
        nullable=False,
        comment="Maximum number of attempts allowed"
    )
    
    allow_late_submission: Mapped[bool] = mapped_column(
        Boolean,
        default=False,
        nullable=False,
        comment="Allow submissions after end_time"
    )
    
    late_penalty_percent: Mapped[Optional[Decimal]] = mapped_column(
        Numeric(5, 2),
        nullable=True,
        comment="Penalty percentage for late submissions"
    )
    
    registration_deadline: Mapped[Optional[datetime]] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
        comment="Deadline for registration"
    )
    
    shuffle_questions: Mapped[bool] = mapped_column(
        Boolean,
        default=False,
        nullable=False,
        comment="Randomize question order for each student"
    )
    
    show_results_immediately: Mapped[bool] = mapped_column(
        Boolean,
        default=False,
        nullable=False,
        comment="Students can see results right after submission"
    )
    
    min_cgpa: Mapped[Optional[Decimal]] = mapped_column(
        Numeric(4, 2),
        nullable=True,
        comment="Minimum CGPA required"
    )
    
    # Proctoring settings
    enable_proctoring: Mapped[bool] = mapped_column(
        Boolean,
        default=False,
        nullable=False,
        comment="Enable proctoring features"
    )
    
    require_webcam: Mapped[bool] = mapped_column(
        Boolean,
        default=False,
        nullable=False,
        comment="Webcam required during assessment"
    )
    
    track_tab_switches: Mapped[bool] = mapped_column(
        Boolean,
        default=False,
        nullable=False,
        comment="Track tab/window switches"
    )

    tab_switch_limit: Mapped[int] = mapped_column(
        Integer,
        default=3,
        nullable=False,
        comment="Maximum number of tab switches allowed"
    )
    
    # Instructions
    instructions: Mapped[Optional[str]] = mapped_column(
        Text,
        nullable=True,
        comment="Assessment instructions (Markdown)"
    )
    
    rules: Mapped[Optional[list[str]]] = mapped_column(
        JSONB,
        default=list,
        nullable=True,
        comment="Assessment rules"
    )
    
    # Statistics
    total_questions: Mapped[int] = mapped_column(
        Integer,
        default=0,
        nullable=False,
        comment="Total number of questions"
    )
    
    total_attempts: Mapped[int] = mapped_column(
        Integer,
        default=0,
        nullable=False,
        comment="Total student attempts"
    )
    
    average_score: Mapped[Optional[Decimal]] = mapped_column(
        Numeric(5, 2),
        nullable=True,
        comment="Average score across all attempts"
    )
    
    # Creator information
    created_by: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("auth.users.id"),
        nullable=False,
        comment="User ID who created this assessment"
    )
    
    # Relationships
    creator: Mapped["AuthUser"] = relationship(
        "AuthUser",
        foreign_keys=[created_by]
    )
    
    question_mappings: Mapped[list["AssessmentQuestion"]] = relationship(
        "AssessmentQuestion",
        back_populates="assessment",
        cascade="all, delete-orphan",
        order_by="AssessmentQuestion.question_order"
    )
    
    attempts: Mapped[list["AssessmentAttempt"]] = relationship(
        "AssessmentAttempt",
        back_populates="assessment",
        cascade="all, delete-orphan"
    )
    
    # Table arguments (indexes)
    __table_args__ = (
        Index("idx_assessment_type", "assessment_type"),
        Index("idx_assessment_published", "is_published", "is_active"),
        Index("idx_assessment_time_range", "start_time", "end_time"),
        Index("idx_assessment_target_branches", "target_branches", postgresql_using="gin"),
    )
    
    def __repr__(self) -> str:
        return f"<Assessment(id={self.id}, title='{self.title[:30]}...', type={self.assessment_type.value})>"
    
    def is_available(self) -> bool:
        """Check if assessment is currently available."""
        if not self.is_published or not self.is_active:
            return False
        now = datetime.utcnow()
        if self.start_time and now < self.start_time:
            return False
        if self.end_time and now > self.end_time:
            return False
        return True
