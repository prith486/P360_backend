"""add_student_indexes

Revision ID: 27ac4840a57d
Revises: 99b3c4f2568c
Create Date: 2026-02-10 23:17:22.654321

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '27ac4840a57d'
down_revision: Union[str, None] = '99b3c4f2568c'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # 1. Single-column B-Tree Indexes
    op.create_index('idx_students_user_id', 'students', ['user_id'])
    op.create_index('idx_students_roll_number', 'students', ['roll_number'])
    op.create_index('idx_students_branch', 'students', ['branch'])
    op.create_index('idx_students_batch_year', 'students', ['batch_year'])
    op.create_index('idx_students_current_year', 'students', ['current_year'])
    op.create_index('idx_students_readiness_score', 'students', [sa.text('readiness_score DESC NULLS LAST')])
    op.create_index('idx_students_cgpa', 'students', [sa.text('cgpa DESC NULLS LAST')])
    op.create_index('idx_students_total_problems_solved', 'students', [sa.text('total_problems_solved DESC')])
    
    # 2. Composite Indexes (B-Tree)
    op.create_index('idx_students_branch_year', 'students', ['branch', 'current_year'])
    op.create_index('idx_students_branch_readiness', 'students', ['branch', sa.text('readiness_score DESC')])
    op.create_index('idx_students_batch_year_branch', 'students', ['batch_year', 'branch'])
    
    # 3. GIN Indexes for JSONB
    op.create_index('idx_students_skills', 'students', ['skills'], postgresql_using='gin')
    op.create_index('idx_students_preferred_roles', 'students', ['preferred_roles'], postgresql_using='gin')
    op.create_index('idx_students_leetcode_stats', 'students', ['leetcode_stats'], postgresql_using='gin')
    
    # 4. Partial Index (B-Tree + WHERE)
    op.create_index(
        'idx_students_active_readiness', 
        'students', 
        [sa.text('readiness_score DESC')], 
        postgresql_where=sa.text("current_year IN ('third', 'fourth')")
    )


def downgrade() -> None:
    op.drop_index('idx_students_active_readiness', table_name='students', postgresql_where=sa.text("current_year IN ('third', 'fourth')"))
    op.drop_index('idx_students_leetcode_stats', table_name='students')
    op.drop_index('idx_students_preferred_roles', table_name='students')
    op.drop_index('idx_students_skills', table_name='students')
    op.drop_index('idx_students_batch_year_branch', table_name='students')
    op.drop_index('idx_students_branch_readiness', table_name='students')
    op.drop_index('idx_students_branch_year', table_name='students')
    op.drop_index('idx_students_total_problems_solved', table_name='students')
    op.drop_index('idx_students_cgpa', table_name='students')
    op.drop_index('idx_students_readiness_score', table_name='students')
    op.drop_index('idx_students_current_year', table_name='students')
    op.drop_index('idx_students_batch_year', table_name='students')
    op.drop_index('idx_students_branch', table_name='students')
    op.drop_index('idx_students_roll_number', table_name='students')
    op.drop_index('idx_students_user_id', table_name='students')
