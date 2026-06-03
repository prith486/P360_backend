"""
Student profile model with external platform stats.
"""

from datetime import datetime
from typing import Optional, Any, TYPE_CHECKING
from decimal import Decimal

import uuid
from sqlalchemy import (
    String, Integer, Numeric, Boolean, DateTime, ForeignKey,
    Enum as SQLEnum, Text, Index, text
)
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import BaseModel
from app.models.enums import BranchType, AcademicYear



if TYPE_CHECKING:
    from app.models.auth_user import AuthUser
    from app.models.submission import Submission
    from app.models.assessment_attempt import AssessmentAttempt


class Student(BaseModel):
    """Student profile model."""
    
    __tablename__ = "students"
    
    # Foreign key to Supabase auth.users
    user_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("auth.users.id", ondelete="CASCADE"),
        unique=True,
        nullable=False,
        comment="Reference to Supabase auth user"
    )

    # Relationships
    user: Mapped["AuthUser"] = relationship(
        "AuthUser",
        # No back_populates needed on AuthUser since it's read-only and we didn't add it there
        # but we can add backref or just keep it one-way if AuthUser doesn't have 'student'
    )
    
    # Academic information
    roll_number: Mapped[str] = mapped_column(
        String(50),
        unique=True,
        nullable=False,
        index=True,
        comment="Student roll number (unique)"
    )
    
    branch: Mapped[BranchType] = mapped_column(
        SQLEnum(BranchType, name="branch_type", values_callable=lambda x: [e.value for e in x], create_type=False),
        nullable=False,
        index=True,
        comment="Academic branch"
    )
    
    batch_year: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
        index=True,
        comment="Batch admission year"
    )
    
    current_year: Mapped[AcademicYear] = mapped_column(
        SQLEnum(AcademicYear, name="academic_year", values_callable=lambda x: [e.value for e in x], create_type=False),
        nullable=False,
        comment="Current academic year"
    )
    
    section: Mapped[Optional[str]] = mapped_column(
        String(10),
        nullable=True,
        comment="Class section"
    )
    
    # Academic performance
    cgpa: Mapped[Optional[Decimal]] = mapped_column(
        Numeric(4, 2),
        nullable=True,
        comment="Current CGPA"
    )
    
    sgpa_sem1: Mapped[Optional[Decimal]] = mapped_column(Numeric(4, 2), nullable=True)
    sgpa_sem2: Mapped[Optional[Decimal]] = mapped_column(Numeric(4, 2), nullable=True)
    sgpa_sem3: Mapped[Optional[Decimal]] = mapped_column(Numeric(4, 2), nullable=True)
    sgpa_sem4: Mapped[Optional[Decimal]] = mapped_column(Numeric(4, 2), nullable=True)
    sgpa_sem5: Mapped[Optional[Decimal]] = mapped_column(Numeric(4, 2), nullable=True)
    sgpa_sem6: Mapped[Optional[Decimal]] = mapped_column(Numeric(4, 2), nullable=True)
    sgpa_sem7: Mapped[Optional[Decimal]] = mapped_column(Numeric(4, 2), nullable=True)
    sgpa_sem8: Mapped[Optional[Decimal]] = mapped_column(Numeric(4, 2), nullable=True)
    
    total_backlogs: Mapped[int] = mapped_column(
        Integer,
        default=0,
        server_default=text("0"),
        nullable=False,
        comment="Total number of backlogs"
    )
    
    active_backlogs: Mapped[int] = mapped_column(
        Integer,
        default=0,
        server_default=text("0"),
        nullable=False,
        comment="Current active backlogs"
    )
    
    # Coding statistics
    total_problems_solved: Mapped[int] = mapped_column(
        Integer,
        default=0,
        server_default=text("0"),
        nullable=False,
        comment="Total problems solved across all platforms"
    )
    
    easy_solved: Mapped[int] = mapped_column(Integer, default=0, server_default=text("0"), nullable=False)
    medium_solved: Mapped[int] = mapped_column(Integer, default=0, server_default=text("0"), nullable=False)
    hard_solved: Mapped[int] = mapped_column(Integer, default=0, server_default=text("0"), nullable=False)
    
    # External platform usernames
    leetcode_username: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    codeforces_username: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    codechef_username: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    geeksforgeeks_username: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    hackerrank_username: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    github_username: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)

    # External platform stats (JSONB)
    leetcode_stats: Mapped[Optional[dict[str, Any]]] = mapped_column(
        JSONB,
        default=dict,
        nullable=True,
        comment="LeetCode statistics (username, problems solved, ranking, etc.)"
    )
    
    codeforces_stats: Mapped[Optional[dict[str, Any]]] = mapped_column(
        JSONB,
        default=dict,
        nullable=True,
        comment="Codeforces statistics"
    )
    
    codechef_stats: Mapped[Optional[dict[str, Any]]] = mapped_column(
        JSONB,
        default=dict,
        nullable=True,
        comment="CodeChef statistics"
    )
    
    geeksforgeeks_stats: Mapped[Optional[dict[str, Any]]] = mapped_column(
        JSONB,
        default=dict,
        nullable=True,
        comment="GeeksforGeeks statistics"
    )
    
    hackerrank_stats: Mapped[Optional[dict[str, Any]]] = mapped_column(
        JSONB,
        default=dict,
        nullable=True,
        comment="HackerRank statistics"
    )

    github_stats: Mapped[Optional[dict[str, Any]]] = mapped_column(
        JSONB,
        default=dict,
        nullable=True,
        comment="GitHub statistics"
    )
    
    # Skills and preferences
    skills: Mapped[Optional[list[str]]] = mapped_column(
        JSONB,
        default=list,
        nullable=True,
        comment="List of technical skills"
    )
    
    preferred_roles: Mapped[Optional[list[str]]] = mapped_column(
        JSONB,
        default=list,
        nullable=True,
        comment="Preferred job roles"
    )
    
    languages_known: Mapped[Optional[list[str]]] = mapped_column(
        JSONB,
        default=list,
        nullable=True,
        comment="Programming languages known"
    )
    
    # Readiness score
    readiness_score: Mapped[Decimal] = mapped_column(
        Numeric(5, 2),
        default=Decimal("0.0"),
        server_default=text("0.0"),
        nullable=False,
        comment="Placement readiness score (0-100)"
    )
    
    last_assessment_date: Mapped[Optional[datetime]] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
        comment="Date of last assessment taken"
    )
    
    last_score_update: Mapped[Optional[datetime]] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
        comment="When readiness score was last calculated"
    )
    
    # Profile Completion
    profile_completion_percent: Mapped[Decimal] = mapped_column(
        Numeric(5, 2),
        default=Decimal("0.00"),
        server_default=text("0.00"),
        nullable=False,
        comment="Profile completion percentage (0-100)"
    )
    
    # Contact information
    personal_email: Mapped[Optional[str]] = mapped_column(
        String(255),
        nullable=True,
        comment="Personal email address"
    )
    
    resume_url: Mapped[Optional[str]] = mapped_column(
        String(500),
        nullable=True,
        comment="Resume URL"
    )
    
    linkedin_url: Mapped[Optional[str]] = mapped_column(
        String(500),
        nullable=True,
        comment="LinkedIn profile URL"
    )
    
    github_url: Mapped[Optional[str]] = mapped_column(
        String(500),
        nullable=True,
        comment="GitHub profile URL"
    )
    
    portfolio_url: Mapped[Optional[str]] = mapped_column(
        String(500),
        nullable=True,
        comment="Personal portfolio URL"
    )
    
    # Placement preferences
    is_placement_ready: Mapped[bool] = mapped_column(
        Boolean,
        default=False,
        server_default=text("false"),
        nullable=False,
        comment="Ready for placement drives"
    )
    
    expected_ctc_min: Mapped[Optional[Decimal]] = mapped_column(
        Numeric(10, 2),
        nullable=True,
        comment="Minimum expected CTC in lakhs"
    )

    expected_ctc_max: Mapped[Optional[Decimal]] = mapped_column(
        Numeric(10, 2),
        nullable=True,
        comment="Maximum expected CTC in lakhs"
    )
    
    willing_to_relocate: Mapped[bool] = mapped_column(
        Boolean,
        default=True,
        server_default=text("true"),
        nullable=False,
        comment="Willing to relocate for job"
    )
    
    # Relationships

    
    submissions: Mapped[list["Submission"]] = relationship(
        "Submission",
        back_populates="student",
        cascade="all, delete-orphan"
    )
    
    assessment_attempts: Mapped[list["AssessmentAttempt"]] = relationship(
        "AssessmentAttempt",
        back_populates="student",
        cascade="all, delete-orphan"
    )
    
    # Table arguments (indexes)
    __table_args__ = (
        Index("idx_student_branch_year", "branch", "batch_year"),
        Index("idx_student_readiness", "readiness_score"),
        Index("idx_student_cgpa", "cgpa"),
        Index("idx_student_placement_ready", "is_placement_ready"),
        Index("idx_student_leetcode_stats", "leetcode_stats", postgresql_using="gin"),
        Index("idx_student_skills", "skills", postgresql_using="gin"),
    )
    
    def __repr__(self) -> str:
        return f"<Student(id={self.id}, roll_number='{self.roll_number}', branch={self.branch.value})>"
    
    def get_external_stats_summary(self) -> dict[str, Any]:
        """Get summary of all external platform stats."""
        return {
            "leetcode": self.leetcode_stats or {},
            "codeforces": self.codeforces_stats or {},
            "codechef": self.codechef_stats or {},
            "geeksforgeeks": self.geeksforgeeks_stats or {},
            "hackerrank": self.hackerrank_stats or {},
        }
