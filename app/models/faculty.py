"""
Faculty profile model.
"""

from typing import Optional, TYPE_CHECKING

import uuid
from sqlalchemy import String, Integer, Boolean, ForeignKey, Text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import BaseModel

if TYPE_CHECKING:
    from app.models.auth_user import AuthUser
    from app.models.question import Question
    from app.models.assessment import Assessment


class Faculty(BaseModel):
    """Faculty profile model."""
    
    __tablename__ = "faculty"
    
    # Foreign key to Supabase auth.users
    user_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("auth.users.id", ondelete="CASCADE"),
        unique=True,
        nullable=False,
        comment="Reference to Supabase auth user"
    )
    
    # Faculty information
    employee_id: Mapped[str] = mapped_column(
        String(50),
        unique=True,
        nullable=False,
        comment="Employee/Faculty ID"
    )
    
    department: Mapped[str] = mapped_column(
        String(100),
        nullable=False,
        comment="Department name"
    )
    
    designation: Mapped[str] = mapped_column(
        String(100),
        nullable=False,
        comment="Job designation"
    )
    
    specialization: Mapped[Optional[str]] = mapped_column(
        Text,
        nullable=True,
        comment="Area of specialization"
    )
    
    # Permissions
    can_create_assessments: Mapped[bool] = mapped_column(
        Boolean,
        default=False,
        nullable=False,
        comment="Permission to create assessments"
    )
    
    can_view_all_students: Mapped[bool] = mapped_column(
        Boolean,
        default=True,
        nullable=False,
        comment="Permission to view all students"
    )
    
    can_grade_submissions: Mapped[bool] = mapped_column(
        Boolean,
        default=True,
        nullable=False,
        comment="Permission to grade submissions"
    )
    
    # Office information
    office_location: Mapped[Optional[str]] = mapped_column(
        String(255),
        nullable=True,
        comment="Office location/room number"
    )
    
    office_hours: Mapped[Optional[str]] = mapped_column(
        Text,
        nullable=True,
        comment="Office hours schedule"
    )
    
    # Relationships
    user: Mapped["AuthUser"] = relationship(
        "AuthUser",
        foreign_keys=[user_id]
    )
    

    
    def __repr__(self) -> str:
        return f"<Faculty(id={self.id}, employee_id='{self.employee_id}', department='{self.department}')>"
