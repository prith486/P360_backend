"""add_performance_indexes

Revision ID: 4c05c11a6b66
Revises: f93f30e4b17c
Create Date: 2026-02-10 22:48:29.167601

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '4c05c11a6b66'
down_revision: Union[str, None] = 'f93f30e4b17c'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # 1. idx_users_email (Assuming non-unique for now, though email col is unique)
    op.create_index('idx_users_email', 'users', ['email'])
    
    # 2. idx_users_role
    op.create_index('idx_users_role', 'users', ['role'])
    
    # 3. idx_users_status
    op.create_index('idx_users_status', 'users', ['status'])
    
    # 4. idx_users_created_at (DESC)
    op.create_index('idx_users_created_at', 'users', [sa.text('created_at DESC')])
    
    # 5. idx_users_last_login (DESC NULLS LAST)
    op.create_index('idx_users_last_login', 'users', [sa.text('last_login DESC NULLS LAST')])
    
    # 6. Composite partial index for active users
    # Note: status enum values are lowercase 'active'
    op.create_index(
        'idx_users_role_status', 
        'users', 
        ['role', 'status'], 
        postgresql_where=sa.text("status = 'active'")
    )


def downgrade() -> None:
    op.drop_index('idx_users_role_status', table_name='users', postgresql_where=sa.text("status = 'active'"))
    op.drop_index('idx_users_last_login', table_name='users')
    op.drop_index('idx_users_created_at', table_name='users')
    op.drop_index('idx_users_status', table_name='users')
    op.drop_index('idx_users_role', table_name='users')
    op.drop_index('idx_users_email', table_name='users')
