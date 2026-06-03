"""
Admin Activity Log model definition.
"""
from sqlalchemy import String, Text, ForeignKey, CheckConstraint, Index, text
from sqlalchemy.dialects.postgresql import INET, UUID as PG_UUID
from sqlalchemy.orm import relationship, Mapped, mapped_column
from uuid import UUID
from app.models.base import BaseModel

class AdminActivityLog(BaseModel):
    """
    Admin activity tracking table for audit trail.
    """
    __tablename__ = "admin_activity_log"

    # Core
    admin_user_id: Mapped[UUID] = mapped_column(PG_UUID(as_uuid=True), ForeignKey("auth.users.id", ondelete="CASCADE"), nullable=False)
    
    # Activity Details
    action_type: Mapped[str] = mapped_column(String(100), nullable=False)
    resource_type: Mapped[str | None] = mapped_column(String(100), nullable=True)
    resource_id: Mapped[UUID | None] = mapped_column(PG_UUID(as_uuid=True), nullable=True)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    
    # Metadata
    ip_address: Mapped[str | None] = mapped_column(INET, nullable=True)
    user_agent: Mapped[str | None] = mapped_column(Text, nullable=True)

    # Relationships
    admin_user = relationship("app.models.auth_user.AuthUser", backref="admin_activities")

    # Constraints and Indexes
    __table_args__ = (
        CheckConstraint(
            "action_type IN ('create', 'update', 'delete', 'export', 'import', 'login', 'logout', 'permission_change', 'bulk_operation')",
            name="check_admin_action_type_valid"
        ),
        # Requested Indexes
        Index('idx_admin_activity_admin_user_id', 'admin_user_id'),
        Index('idx_admin_activity_action_type', 'action_type'),
        Index('idx_admin_activity_created_at', text('created_at DESC')),
        Index('idx_admin_activity_resource', 'resource_type', 'resource_id'),
    )
