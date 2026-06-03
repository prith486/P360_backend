"""add_performance_composite_indexes

Revision ID: d4521ae20bf4
Revises: b3704704a098
Create Date: 2026-02-11 00:03:00.123456

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'd4521ae20bf4'
down_revision: Union[str, None] = 'b3704704a098'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # 1. Leaderboard index for students
    op.create_index(
        'idx_students_leaderboard', 
        'students', 
        ['batch_year', 'branch', sa.text('readiness_score DESC'), sa.text('total_problems_solved DESC')]
    )

    # 2. Active assessment participants index (Partial)
    op.create_index(
        'idx_active_assessments_participants',
        'assessment_attempts',
        ['assessment_id', sa.text('submitted_at DESC')],
        postgresql_where=sa.text('submitted_at IS NOT NULL')
    )

    # 3. Student submission history index (Covering index with INCLUDE)
    op.create_index(
        'idx_student_submission_history',
        'submissions',
        ['student_id', sa.text('submitted_at DESC'), 'status'],
        postgresql_include=['question_id', 'score']
    )

    # 4. Faculty assessment management index (Partial)
    op.create_index(
        'idx_faculty_assessments',
        'assessments',
        ['created_by', 'is_published', sa.text('created_at DESC')],
        postgresql_where=sa.text('is_active = TRUE')
    )

    # 5. Question bank filtering index (Partial)
    op.create_index(
        'idx_question_bank',
        'questions',
        ['difficulty', 'question_type', 'is_active'],
        postgresql_where=sa.text('is_public = TRUE')
    )


def downgrade() -> None:
    op.drop_index('idx_question_bank', table_name='questions')
    op.drop_index('idx_faculty_assessments', table_name='assessments')
    op.drop_index('idx_student_submission_history', table_name='submissions')
    op.drop_index('idx_active_assessments_participants', table_name='assessment_attempts')
    op.drop_index('idx_students_leaderboard', table_name='students')
