"""
Database enums matching PostgreSQL schema.
"""

from enum import Enum as PyEnum


class UserRole(str, PyEnum):
    """User role types."""
    STUDENT = "student"
    FACULTY = "faculty"
    ADMIN = "admin"


class UserStatus(str, PyEnum):
    """User account status."""
    ACTIVE = "active"
    INACTIVE = "inactive"
    SUSPENDED = "suspended"


class BranchType(str, PyEnum):
    """Academic branch types."""
    COMPUTER_SCIENCE = "computer_science"
    INFORMATION_TECHNOLOGY = "information_technology"
    ELECTRONICS = "electronics"
    MECHANICAL = "mechanical"
    CIVIL = "civil"
    ELECTRICAL = "electrical"
    AI_ML = "ai_ml"


class AcademicYear(str, PyEnum):
    """Academic year levels."""
    FIRST = "first"
    SECOND = "second"
    THIRD = "third"
    FOURTH = "fourth"


class DifficultyLevel(str, PyEnum):
    """Question difficulty levels."""
    EASY = "easy"
    MEDIUM = "medium"
    HARD = "hard"
    EXPERT = "expert"


class QuestionType(str, PyEnum):
    """Question types."""
    CODING = "coding"
    MCQ = "mcq"
    SUBJECTIVE = "subjective"


class AssessmentType(str, PyEnum):
    """Assessment types."""
    MOCK_TEST = "mock_test"
    PRACTICE = "practice"
    CONTEST = "contest"
    PLACEMENT = "placement"
    PLACEMENT_TEST = "placement_test"
    MCQ = "MCQ"
    CODING = "Coding"
    MIXED = "Mixed"


class SubmissionStatus(str, PyEnum):
    """Submission status from Judge0."""
    PENDING = "pending"
    PROCESSING = "processing"
    ACCEPTED = "accepted"
    WRONG_ANSWER = "wrong_answer"
    TIME_LIMIT_EXCEEDED = "time_limit_exceeded"
    COMPILATION_ERROR = "compilation_error"
    RUNTIME_ERROR = "runtime_error"
    INTERNAL_ERROR = "internal_error"


class ProgrammingLanguage(str, PyEnum):
    """Supported programming languages."""
    PYTHON = "python"
    JAVA = "java"
    CPP = "cpp"
    JAVASCRIPT = "javascript"
    C = "c"
    CSHARP = "csharp"
    GO = "go"
    RUST = "rust"
