"""add_questions_indexes

Revision ID: b5cc062c4e69
Revises: 279350d0557c
Create Date: 2026-02-10 23:43:41.123456

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'b5cc062c4e69'
down_revision: Union[str, None] = '279350d0557c'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Single-column indexes
    op.create_index('idx_questions_difficulty', 'questions', ['difficulty'])
    op.create_index('idx_questions_question_type', 'questions', ['question_type'])
    op.create_index('idx_questions_slug', 'questions', ['slug'])
    op.create_index('idx_questions_created_by', 'questions', ['created_by'])
    
    # Partial indexes for active/public questions
    op.create_index('idx_questions_is_active', 'questions', ['is_active'], postgresql_where=sa.text('is_active = TRUE'))
    op.create_index('idx_questions_is_public', 'questions', ['is_public'], postgresql_where=sa.text('is_public = TRUE'))
    
    # GIN indexes for JSONB tag searches
    op.create_index('idx_questions_tags', 'questions', ['tags'], postgresql_using='gin')
    op.create_index('idx_questions_topics', 'questions', ['topics'], postgresql_using='gin')
    op.create_index('idx_questions_company_tags', 'questions', ['company_tags'], postgresql_using='gin')


def downgrade() -> None:
    op.drop_index('idx_questions_company_tags', table_name='questions', postgresql_using='gin')
    op.drop_index('idx_questions_topics', table_name='questions', postgresql_using='gin')
    op.drop_index('idx_questions_tags', table_name='questions', postgresql_using='gin')
    op.drop_index('idx_questions_is_public', table_name='questions', postgresql_where=sa.text('is_public = TRUE'))
    op.drop_index('idx_questions_is_active', table_name='questions', postgresql_where=sa.text('is_active = TRUE'))
    op.drop_index('idx_questions_created_by', table_name='questions')
    op.drop_index('idx_questions_slug', table_name='questions')
    op.drop_index('idx_questions_question_type', table_name='questions')
    op.drop_index('idx_questions_difficulty', table_name='questions')
