"""
Read-only reference to Supabase auth.users.
DO NOT use for creating/updating users - use Supabase client instead.
"""
import uuid
from typing import Optional, Any
from datetime import datetime, timezone

from sqlalchemy import String, Integer, Boolean, DateTime, UniqueConstraint, Index
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.orm import Mapped, mapped_column

from app.models.base import Base

class AuthUser(Base):
    """Read-only model for Supabase auth.users table."""
    
    __tablename__ = "users"
    __table_args__ = (
        {"schema": "auth"}
    )
    
    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True)
    instance_id: Mapped[Optional[uuid.UUID]] = mapped_column(UUID(as_uuid=True))
    email: Mapped[Optional[str]] = mapped_column(String(255))
    role: Mapped[Optional[str]] = mapped_column(String(255))
    aud: Mapped[Optional[str]] = mapped_column(String(255))
    
    # Sensitive fields shouldn't be loaded typically, but mapped for ORM correctness if needed
    encrypted_password: Mapped[Optional[str]] = mapped_column(String(255))
    
    email_confirmed_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True))
    invited_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True))
    confirmation_token: Mapped[Optional[str]] = mapped_column(String(255))
    confirmation_sent_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True))
    recovery_token: Mapped[Optional[str]] = mapped_column(String(255))
    recovery_sent_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True))
    email_change_token_new: Mapped[Optional[str]] = mapped_column(String(255))
    email_change: Mapped[Optional[str]] = mapped_column(String(255))
    email_change_sent_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True))
    last_sign_in_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True))
    
    raw_app_meta_data: Mapped[Optional[dict[str, Any]]] = mapped_column(JSONB)
    raw_user_meta_data: Mapped[Optional[dict[str, Any]]] = mapped_column(JSONB)
    
    is_super_admin: Mapped[Optional[bool]] = mapped_column(Boolean)
    
    created_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True))
    updated_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True))
    
    phone: Mapped[Optional[str]] = mapped_column(String(15))
    phone_confirmed_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True))
    phone_change: Mapped[Optional[str]] = mapped_column(String(15))
    phone_change_token: Mapped[Optional[str]] = mapped_column(String(255))
    phone_change_sent_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True))
    
    confirmed_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True))
    email_change_token_current: Mapped[Optional[str]] = mapped_column(String(255))
    email_change_confirm_status: Mapped[Optional[int]] = mapped_column(Integer)
    banned_until: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True))
    reauthentication_token: Mapped[Optional[str]] = mapped_column(String(255))
    reauthentication_sent_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True))
    
    is_sso_user: Mapped[bool] = mapped_column(Boolean, default=False)
    deleted_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True))
    
    @property
    def full_name(self) -> str:
        """Get full name from raw_user_meta_data."""
        if not self.raw_user_meta_data:
            return ""
        
        # Check different common keys in Supabase/GoTrue
        first = self.raw_user_meta_data.get("firstName") or self.raw_user_meta_data.get("first_name") or ""
        last = self.raw_user_meta_data.get("lastName") or self.raw_user_meta_data.get("last_name") or ""
        full = self.raw_user_meta_data.get("full_name") or self.raw_user_meta_data.get("name") or ""
        
        if full:
            return full
        if first or last:
            return f"{first} {last}".strip()
        return ""

    @full_name.setter
    def full_name(self, value: str):
        """Allow setting full name back into metadata."""
        if self.raw_user_meta_data is None:
            self.raw_user_meta_data = {}
        self.raw_user_meta_data["full_name"] = value
    
    def __repr__(self) -> str:
        return f"<AuthUser(id={self.id}, email='{self.email}')>"

    @property
    def computed_role(self) -> str:
        """Get application role from metadata. Used for UserRead mapping."""
        if self.raw_app_meta_data:
            return self.raw_app_meta_data.get("role", self.role or "authenticated")
        return self.role or "authenticated"

    @property
    def role_name(self) -> str:
        """Alias for UserRead compatibility."""
        return self.computed_role

    @property
    def is_account_active(self) -> bool:
        """Boolean property for UserRead."""
        if self.deleted_at is not None:
            return False
        if self.banned_until is not None and self.banned_until > datetime.now(timezone.utc):
            return False
        return True
    
    @property
    def is_active(self) -> bool:
        """Alias for is_account_active for backward compatibility."""
        return self.is_account_active
