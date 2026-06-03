"""add_submissions_indexes

Revision ID: 2c71cda2be60
Revises: 7c2fa130e6d5
Create Date: 2026-02-10 23:55:55.123456

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '2c71cda2be60'
down_revision: Union[str, None] = '7c2fa130e6d5'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # 1. Single-column indexes
    op.create_index('idx_submissions_student_id', 'submissions', ['student_id'])
    op.create_index('idx_submissions_question_id', 'submissions', ['question_id'])
    op.create_index('idx_submissions_assessment_id', 'submissions', ['assessment_id'])
    op.create_index('idx_submissions_status', 'submissions', ['status'])
    op.create_index('idx_submissions_submitted_at', 'submissions', [sa.text('submitted_at DESC')])
    op.create_index('idx_submissions_language', 'submissions', ['language'])
    
    # 2. Composite indexes for common queries
    op.create_index('idx_submissions_student_question', 'submissions', ['student_id', 'question_id'])
    op.create_index('idx_submissions_student_assessment', 'submissions', ['student_id', 'assessment_id'])
    op.create_index('idx_submissions_question_status', 'submissions', ['question_id', 'status'])
    
    # 3. Composite index for leaderboard queries (best submission per student-question)
    op.create_index('idx_submissions_best_score', 'submissions', ['student_id', 'question_id', sa.text('score DESC')])


def downgrade() -> None:
    op.drop_index('idx_submissions_best_score', table_name='submissions')
    op.drop_index('idx_submissions_question_status', table_name='submissions')
    op.drop_index('idx_submissions_student_assessment', table_name='submissions')
    op.drop_index('idx_submissions_student_question', table_name='submissions')
    op.drop_index('idx_submissions_language', table_name='submissions')
    op.drop_index('idx_submissions_submitted_at', table_name='submissions')
    op.drop_index('idx_submissions_status', table_name='submissions')
    op.drop_index('idx_submissions_assessment_id', table_name='submissions')
    op.drop_index('idx_submissions_question_id', table_name='submissions')
    op.drop_index('idx_submissions_student_id', table_name='submissions')
