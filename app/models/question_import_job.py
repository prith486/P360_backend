"""Question import job model for bulk upload workflows."""

from enum import Enum as PyEnum
from typing import Any, Optional, TYPE_CHECKING
import uuid

from sqlalchemy import String, Integer, Enum as SQLEnum, ForeignKey, Index
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import BaseModel

if TYPE_CHECKING:
    from app.models.auth_user import AuthUser


class ImportFileType(str, PyEnum):
    """Supported import file types."""

    XLSX = "xlsx"
    CSV = "csv"
    PDF = "pdf"


class ImportJobStatus(str, PyEnum):
    """Lifecycle states for an import job."""

    PENDING = "pending"
    PROCESSING = "processing"
    AWAITING_REVIEW = "awaiting_review"
    COMPLETED = "completed"
    FAILED = "failed"


class QuestionImportJob(BaseModel):
    """Tracks bulk question import processing and review state."""

    __tablename__ = "question_import_jobs"

    faculty_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("auth.users.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
        comment="Faculty user ID who initiated import",
    )

    file_type: Mapped[ImportFileType] = mapped_column(
        SQLEnum(
            ImportFileType,
            name="question_import_file_type",
            values_callable=lambda x: [e.value for e in x],
            create_type=False,
        ),
        nullable=False,
        comment="Input file type",
    )

    original_filename: Mapped[str] = mapped_column(
        String(255),
        nullable=False,
        comment="Original uploaded filename",
    )

    status: Mapped[ImportJobStatus] = mapped_column(
        SQLEnum(
            ImportJobStatus,
            name="question_import_status",
            values_callable=lambda x: [e.value for e in x],
            create_type=False,
        ),
        nullable=False,
        default=ImportJobStatus.PENDING,
        index=True,
        comment="Processing status",
    )

    total_rows: Mapped[Optional[int]] = mapped_column(
        Integer,
        nullable=True,
        comment="Total parsed rows/items from file",
    )

    imported_count: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
        default=0,
        comment="Count of rows saved as questions",
    )

    failed_rows: Mapped[list[dict[str, Any]]] = mapped_column(
        JSONB,
        nullable=False,
        default=list,
        comment="Rows that failed validation with reasons",
    )

    parsed_preview: Mapped[Optional[list[dict[str, Any]]]] = mapped_column(
        JSONB,
        nullable=True,
        default=list,
        comment="Parsed rows preview pending faculty confirmation",
    )

    faculty: Mapped["AuthUser"] = relationship("AuthUser", foreign_keys=[faculty_id])

    __table_args__ = (
        Index("idx_question_import_jobs_created_at", "created_at"),
    )

    def __repr__(self) -> str:
        return (
            f"<QuestionImportJob(id={self.id}, faculty_id={self.faculty_id}, "
            f"status={self.status.value})>"
        )
