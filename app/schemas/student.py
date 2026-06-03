"""
Pydantic schemas for Student profile operations.
"""

from typing import Optional, List, Dict, Any
from datetime import datetime
from decimal import Decimal
import uuid

from pydantic import BaseModel, Field, EmailStr, field_validator, ConfigDict

from app.models.enums import BranchType, AcademicYear


# ============================================================================
# BASE SCHEMAS
# ============================================================================

class StudentBase(BaseModel):
    """Base student schema with common fields."""
    
    roll_number: str = Field(..., min_length=5, max_length=50, description="Student roll number")
    branch: BranchType = Field(..., description="Engineering branch")
    batch_year: int = Field(..., ge=2020, le=2050, description="Batch year")
    current_year: AcademicYear = Field(..., description="Current academic year")
    cgpa: Optional[Decimal] = Field(None, ge=0, le=10, description="CGPA out of 10")
    
    @field_validator("cgpa")
    @classmethod
    def validate_cgpa_precision(cls, v: Optional[Decimal]) -> Optional[Decimal]:
        """Validate CGPA has at most 2 decimal places."""
        if v is not None:
            # Check decimal places
            if v.as_tuple().exponent < -2:
                raise ValueError("CGPA must have at most 2 decimal places")
        return v


# ============================================================================
# READ SCHEMAS (Response Models)
# ============================================================================

class ExternalPlatformStats(BaseModel):
    """External platform statistics schema."""
    
    easy: Optional[int] = Field(None, description="Easy problems solved")
    medium: Optional[int] = Field(None, description="Medium problems solved")
    hard: Optional[int] = Field(None, description="Hard problems solved")
    total: Optional[int] = Field(None, description="Total problems solved")
    rank: Optional[int] = Field(None, description="Platform rank")
    rating: Optional[int] = Field(None, description="Platform rating")
    contests: Optional[int] = Field(None, description="Contests participated")
    
    model_config = ConfigDict(extra='allow')  # Allow additional fields


class StudentRead(BaseModel):
    """Student profile response schema."""
    
    id: uuid.UUID
    user_id: uuid.UUID
    roll_number: str
    branch: BranchType
    batch_year: int
    current_year: AcademicYear
    cgpa: Optional[Decimal] = None
    
    # --- User identity fields (populated from auth.users at endpoint level) ---
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    email: Optional[str] = None
    role: Optional[str] = "student"
    phone_number: Optional[str] = None
    avatar_url: Optional[str] = None
    # Convenience alias matching frontend usage (same value as current_year.value)
    year: Optional[str] = None
    # -------------------------------------------------------------------------
    
    # Readiness and scores
    readiness_score: Optional[Decimal] = Field(default=Decimal("0"), description="Placement readiness score (0-100)")
    last_assessment_date: Optional[datetime] = None
    
    # External platform usernames
    leetcode_username: Optional[str] = None
    codeforces_username: Optional[str] = None
    codechef_username: Optional[str] = None
    geeksforgeeks_username: Optional[str] = None
    hackerrank_username: Optional[str] = None
    github_username: Optional[str] = None
    
    # External platform statistics (JSONB fields)
    leetcode_stats: Optional[Dict[str, Any]] = Field(default_factory=dict)
    codeforces_stats: Optional[Dict[str, Any]] = Field(default_factory=dict)
    codechef_stats: Optional[Dict[str, Any]] = Field(default_factory=dict)
    geeksforgeeks_stats: Optional[Dict[str, Any]] = Field(default_factory=dict)
    hackerrank_stats: Optional[Dict[str, Any]] = Field(default_factory=dict)
    github_stats: Optional[Dict[str, Any]] = Field(default_factory=dict)
    
    # Aggregated view for frontend
    platform_stats: Optional[Dict[str, Any]] = Field(default_factory=dict)
    
    # Resume and portfolio
    resume_url: Optional[str] = None
    portfolio_url: Optional[str] = None
    linkedin_url: Optional[str] = None
    
    # Skills and preferences
    skills: Optional[List[str]] = Field(default_factory=list)
    preferred_roles: Optional[List[str]] = Field(default_factory=list)
    languages_known: Optional[List[str]] = Field(default_factory=list)
    section: Optional[str] = None
    
    # CTC expectations
    expected_ctc_min: Optional[Decimal] = None
    expected_ctc_max: Optional[Decimal] = None
    
    # Statistics cache
    total_problems_solved: int = 0
    easy_solved: int = 0
    medium_solved: int = 0
    hard_solved: int = 0
    
    # Profile completion
    profile_completion_percent: Optional[Decimal] = Field(default=Decimal("0"))
    
    # Status (computed at endpoint level)
    status: Optional[str] = None
    
    # Timestamps
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

    @field_validator('languages_known', mode='before')
    @classmethod
    def validate_languages_known(cls, v):
        return v if v is not None else []
    
    @field_validator('github_stats', mode='before')
    @classmethod
    def validate_github_stats(cls, v):
        return v if v is not None else {}
    
    @field_validator('skills', mode='before')
    @classmethod
    def validate_skills(cls, v):
        return v if v is not None else []
    
    @field_validator('preferred_roles', mode='before')
    @classmethod
    def validate_preferred_roles(cls, v):
        return v if v is not None else []
    
    @field_validator('leetcode_stats', mode='before')
    @classmethod
    def validate_leetcode_stats(cls, v):
        return v if v is not None else {}
    
    @field_validator('codeforces_stats', mode='before')
    @classmethod
    def validate_codeforces_stats(cls, v):
        return v if v is not None else {}
    
    @field_validator('codechef_stats', mode='before')
    @classmethod
    def validate_codechef_stats(cls, v):
        return v if v is not None else {}
    
    @field_validator('geeksforgeeks_stats', mode='before')
    @classmethod
    def validate_geeksforgeeks_stats(cls, v):
        return v if v is not None else {}
    
    @field_validator('hackerrank_stats', mode='before')
    @classmethod
    def validate_hackerrank_stats(cls, v):
        return v if v is not None else {}
    
    model_config = ConfigDict(from_attributes=True)


class StudentDetailedRead(StudentRead):
    """
    Detailed student profile with user information.
    Includes email, full name, and other user details.
    """
    
    # User information
    email: Optional[str] = None
    full_name: Optional[str] = None
    phone: Optional[str] = None
    
    # User status
    email_verified: Optional[bool] = None
    account_status: Optional[str] = None
    
    # Assessment Performance (Faculty View)
    assessment_attempts: Optional[List[Dict[str, Any]]] = Field(default_factory=list)
    assessment_count: int = 0
    average_score: float = 0.0


# ============================================================================
# WRITE SCHEMAS (Request Models)
# ============================================================================

class StudentUpdate(BaseModel):
    """Student profile update schema."""
    
    # Note: roll_number, branch, batch_year are immutable
    current_year: Optional[AcademicYear] = None
    cgpa: Optional[Decimal] = Field(None, ge=0, le=10)
    
    # External platform usernames (nullable for disconnecting)
    leetcode_username: Optional[str] = Field(None, max_length=100)
    codeforces_username: Optional[str] = Field(None, max_length=100)
    codechef_username: Optional[str] = Field(None, max_length=100)
    geeksforgeeks_username: Optional[str] = Field(None, max_length=100)
    hackerrank_username: Optional[str] = Field(None, max_length=100)
    github_username: Optional[str] = Field(None, max_length=100)
    
    # Resume and portfolio
    resume_url: Optional[str] = Field(None, max_length=500)
    portfolio_url: Optional[str] = Field(None, max_length=500)
    linkedin_url: Optional[str] = Field(None, max_length=500)
    
    # Skills and preferences
    skills: Optional[List[str]] = Field(None, max_items=50)
    preferred_roles: Optional[List[str]] = Field(None, max_items=20)
    
    # CTC expectations
    expected_ctc_min: Optional[Decimal] = Field(None, ge=0)
    expected_ctc_max: Optional[Decimal] = Field(None, ge=0)
    
    @field_validator("cgpa")
    @classmethod
    def validate_cgpa_precision(cls, v: Optional[Decimal]) -> Optional[Decimal]:
        """Validate CGPA has at most 2 decimal places."""
        if v is not None and v.as_tuple().exponent < -2:
            raise ValueError("CGPA must have at most 2 decimal places")
        return v
    
    @field_validator("expected_ctc_max")
    @classmethod
    def validate_ctc_range(cls, v: Optional[Decimal], info) -> Optional[Decimal]:
        """Validate max CTC is greater than or equal to min CTC."""
        if v is not None and info.data.get("expected_ctc_min") is not None:
            if v < info.data["expected_ctc_min"]:
                raise ValueError("Maximum CTC must be greater than or equal to minimum CTC")
        return v
    
    @field_validator("skills")
    @classmethod
    def validate_skills_not_empty(cls, v: Optional[List[str]]) -> Optional[List[str]]:
        """Validate skills list has no empty strings."""
        if v is not None:
            if any(not skill.strip() for skill in v):
                raise ValueError("Skills cannot contain empty strings")
        return v


class ExternalPlatformConnect(BaseModel):
    """Schema for connecting external platform username."""
    
    platform: str = Field(
        ..., 
        description="Platform name: leetcode, codeforces, codechef, geeksforgeeks, hackerrank, github"
    )
    username: str = Field(..., min_length=1, max_length=100, description="Platform username")
    
    @field_validator("platform")
    @classmethod
    def validate_platform(cls, v: str) -> str:
        """Validate platform is supported."""
        supported_platforms = [
            "leetcode", "codeforces", "codechef", 
            "geeksforgeeks", "hackerrank", "github"
        ]
        if v.lower() not in supported_platforms:
            raise ValueError(
                f"Platform must be one of: {', '.join(supported_platforms)}"
            )
        return v.lower()


class ExternalPlatformDisconnect(BaseModel):
    """Schema for disconnecting external platform."""
    
    platform: str = Field(
        ...,
        description="Platform to disconnect: leetcode, codeforces, codechef, geeksforgeeks, hackerrank, github"
    )
    
    @field_validator("platform")
    @classmethod
    def validate_platform(cls, v: str) -> str:
        """Validate platform is supported."""
        supported_platforms = [
            "leetcode", "codeforces", "codechef",
            "geeksforgeeks", "hackerrank", "github"
        ]
        if v.lower() not in supported_platforms:
            raise ValueError(
                f"Platform must be one of: {', '.join(supported_platforms)}"
            )
        return v.lower()

# ============================================================================
# LEGACY / ADDITIONAL SCHEMAS
# ============================================================================

class StudentCreate(StudentBase):
    """Schema for creating student profile."""
    user_id: uuid.UUID
    pass

class StudentLeaderboard(BaseModel):
    """Schema for leaderboard views."""
    id: uuid.UUID
    roll_number: str
    full_name: str
    branch: BranchType
    total_problems_solved: int
    easy_solved: int
    medium_solved: int
    hard_solved: int
    readiness_score: Decimal
    rank: Optional[int] = None
    
    model_config = ConfigDict(from_attributes=True)


# ============================================================================
# FACULTY MANAGEMENT SCHEMAS
# ============================================================================

class StudentFacultyUpdate(BaseModel):
    """Schema for faculty updating a student's profile."""
    cgpa: Optional[float] = Field(None, ge=0, le=10)
    is_placement_ready: Optional[bool] = None
    readiness_score: Optional[float] = Field(None, ge=0, le=100)
    skills: Optional[List[str]] = None
    preferred_roles: Optional[List[str]] = None
    current_year: Optional[AcademicYear] = None
    section: Optional[str] = None

class StudentCreateByFaculty(BaseModel):
    """Schema for faculty manually registering a student."""
    email: EmailStr
    full_name: str
    roll_number: str
    branch: BranchType
    batch_year: int
    current_year: AcademicYear
    cgpa: Optional[float] = Field(None, ge=0, le=10)
    section: Optional[str] = None
