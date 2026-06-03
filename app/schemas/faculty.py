"""
Pydantic schemas for Faculty model.
"""
import uuid
from datetime import datetime
from typing import Optional

from pydantic import BaseModel, Field, ConfigDict

from app.schemas.user import UserRead


class FacultyBase(BaseModel):
    """Base schema with common faculty fields."""
    employee_id: str = Field(..., min_length=3, max_length=50)
    department: Optional[str] = Field(None, max_length=100)
    designation: Optional[str] = Field(None, max_length=100)


class FacultyCreate(FacultyBase):
    """Schema for creating faculty profile."""
    user_id: uuid.UUID


class FacultyUpdate(BaseModel):
    """Schema for updating faculty profile."""
    department: Optional[str] = Field(None, max_length=100)
    designation: Optional[str] = Field(None, max_length=100)
    office_location: Optional[str] = Field(None, max_length=255)
    office_hours: Optional[str] = None


class FacultyRead(FacultyBase):
    """Schema for faculty response."""
    id: uuid.UUID
    user_id: uuid.UUID
    office_location: Optional[str] = None
    office_hours: Optional[str] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    
    model_config = ConfigDict(from_attributes=True)


class FacultyDetailed(FacultyRead):
    """Detailed schema including user info."""
    user: UserRead
    
    model_config = ConfigDict(from_attributes=True)
