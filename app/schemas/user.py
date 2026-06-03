"""
Pydantic schemas for User model.
"""

import uuid
from datetime import datetime
from typing import Optional, Any

from pydantic import BaseModel, EmailStr, Field, ConfigDict

from app.models.enums import UserRole, UserStatus


class UserBase(BaseModel):
    """Base schema with common user fields."""
    email: EmailStr
    full_name: str = Field(..., min_length=2, max_length=255)
    phone_number: Optional[str] = Field(None, max_length=15)
    profile_picture_url: Optional[str] = Field(None, max_length=500)


class UserCreate(UserBase):
    """Schema for creating new user."""
    password: str = Field(..., min_length=8, max_length=128)
    role: UserRole = UserRole.STUDENT


class UserUpdate(BaseModel):
    """Schema for updating user profile."""
    full_name: Optional[str] = Field(None, min_length=2, max_length=255)
    phone_number: Optional[str] = Field(None, max_length=15)
    profile_picture_url: Optional[str] = Field(None, max_length=500)


class PasswordChange(BaseModel):
    """Schema for password change."""
    old_password: str = Field(..., min_length=8)
    new_password: str = Field(..., min_length=8, max_length=128)


class UserRead(BaseModel):
    """Schema for user response (AuthUser compatible)."""
    id: uuid.UUID
    email: str
    full_name: Optional[str] = ""
    role: str = "authenticated"
    is_active: bool = True
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    email_confirmed_at: Optional[datetime] = None

    model_config = ConfigDict(from_attributes=True)
    
    @classmethod
    def from_auth_user(cls, auth_user):
        """Create UserRead from AuthUser with proper field mapping."""
        return cls(
            id=auth_user.id,
            email=auth_user.email or "",
            full_name=auth_user.full_name or "",
            role=auth_user.computed_role if hasattr(auth_user, 'computed_role') else "authenticated",
            is_active=auth_user.is_active if hasattr(auth_user, 'is_active') else True,
            created_at=auth_user.created_at,
            updated_at=auth_user.updated_at,
            email_confirmed_at=auth_user.email_confirmed_at
        )
