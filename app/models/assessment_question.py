"""
Many-to-many mapping between assessments and questions.
"""

from typing import TYPE_CHECKING

import uuid
from sqlalchemy import Integer, ForeignKey, UniqueConstraint, Index
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import BaseModel

if TYPE_CHECKING:
    from app.models.assessment import Assessment
    from app.models.question import Question


class AssessmentQuestion(BaseModel):
    """Maps questions to assessments with ordering and marks."""
    
    __tablename__ = "assessment_questions"
    
    # Foreign keys
    assessment_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("assessments.id", ondelete="CASCADE"),
        nullable=False,
        comment="Reference to assessment"
    )
    
    question_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("questions.id", ondelete="CASCADE"),
        nullable=False,
        comment="Reference to question"
    )
    
    # Ordering and marks
    question_order: Mapped[int] = mapped_column(
        Integer,
        default=1,
        nullable=False,
        comment="Order of question in assessment"
    )
    
    marks: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
        comment="Marks allocated for this question"
    )
    
    # Relationships
    assessment: Mapped["Assessment"] = relationship(
        "Assessment",
        back_populates="question_mappings"
    )
    
    question: Mapped["Question"] = relationship(
        "Question",
        back_populates="assessment_mappings"
    )
    
    # Table arguments
    __table_args__ = (
        UniqueConstraint("assessment_id", "question_id", name="uq_assessment_question"),
        Index("idx_assessment_question_order", "assessment_id", "question_order"),
    )
    
    def __repr__(self) -> str:
        return f"<AssessmentQuestion(assessment_id={self.assessment_id}, question_id={self.question_id}, order={self.question_order})>"
