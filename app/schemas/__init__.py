"""
Schemas package initialization.
"""

from app.schemas.user import (
    UserCreate,
    UserRead,
    UserUpdate,
    PasswordChange,
)
from app.schemas.student import (
    StudentBase,
    StudentRead,
    StudentDetailedRead,
    StudentUpdate,
    ExternalPlatformConnect,
    ExternalPlatformDisconnect,
    ExternalPlatformStats,
    StudentCreate,
    StudentLeaderboard
)
from app.schemas.question import (
    QuestionCreate,
    QuestionRead,
    QuestionUpdate,
    QuestionDetailed,
)
from app.schemas.submission import (
    SubmissionCreate,
    SubmissionRead,
    SubmissionDetailed,
)

__all__ = [
    # User schemas
    "UserCreate",
    "UserRead",
    "UserUpdate",
    "PasswordChange",
    # Student schemas
    "StudentCreate",
    "StudentRead",
    "StudentUpdate",
    "StudentDetailed",
    "StudentLeaderboard",
    "ExternalStatsUpdate",
    # Question schemas
    "QuestionCreate",
    "QuestionRead",
    "QuestionUpdate",
    "QuestionDetailed",
    # Submission schemas
    "SubmissionCreate",
    "SubmissionRead",
    "SubmissionDetailed",
]
