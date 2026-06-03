"""
Models package initialization.
Import all models for Alembic auto-detection.
"""

from app.models.base import Base, BaseModel, TimestampMixin
from app.models.enums import (
    UserRole,
    UserStatus,
    BranchType,
    AcademicYear,
    DifficultyLevel,
    QuestionType,
    AssessmentType,
    SubmissionStatus,
    ProgrammingLanguage,
)
from app.models.auth_user import AuthUser
from app.models.student import Student
from app.models.faculty import Faculty
from app.models.question import Question
from app.models.assessment import Assessment
from app.models.assessment_question import AssessmentQuestion
from app.models.submission import Submission
from app.models.assessment_attempt import AssessmentAttempt
from app.models.question_import_job import QuestionImportJob

__all__ = [
    # ...
    # Models
    "AuthUser",
    "Student",
    "Faculty",
    "Question",
    "Assessment",
    "AssessmentQuestion",
    "Submission",
    "AssessmentAttempt",
    "QuestionImportJob",
]
