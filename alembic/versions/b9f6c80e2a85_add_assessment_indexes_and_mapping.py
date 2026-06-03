"""add_assessment_indexes_and_mapping

Revision ID: b9f6c80e2a85
Revises: bd2e785c8e0c
Create Date: 2026-02-10 23:48:36.123456

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'b9f6c80e2a85'
down_revision: Union[str, None] = 'bd2e785c8e0c'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # 1. Create indexes for assessments table
    op.create_index('idx_assessments_slug', 'assessments', ['slug'])
    op.create_index('idx_assessments_assessment_type', 'assessments', ['assessment_type'])
    op.create_index('idx_assessments_start_time', 'assessments', ['start_time'])
    op.create_index('idx_assessments_end_time', 'assessments', ['end_time'])
    op.create_index('idx_assessments_created_by', 'assessments', ['created_by'])
    op.create_index('idx_assessments_is_published', 'assessments', ['is_published'], postgresql_where=sa.text('is_published = TRUE'))
    op.create_index('idx_assessments_active_published', 'assessments', ['is_active', 'is_published'], postgresql_where=sa.text('is_active = TRUE AND is_published = TRUE'))
    
    # 2. Create assessment_questions mapping table
    op.create_table('assessment_questions',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('assessment_id', sa.Integer(), nullable=False),
    sa.Column('question_id', sa.Integer(), nullable=False),
    sa.Column('question_order', sa.Integer(), nullable=False),
    sa.Column('marks', sa.Integer(), server_default=sa.text('10'), nullable=False),
    sa.Column('is_mandatory', sa.Boolean(), server_default=sa.text('true'), nullable=True),
    sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
    sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
    sa.CheckConstraint('marks > 0', name='check_assessment_questions_marks_positive'),
    sa.ForeignKeyConstraint(['assessment_id'], ['assessments.id'], ondelete='CASCADE'),
    sa.ForeignKeyConstraint(['question_id'], ['questions.id'], ondelete='CASCADE'),
    sa.PrimaryKeyConstraint('id'),
    sa.UniqueConstraint('assessment_id', 'question_id', name='uq_assessment_question'),
    sa.UniqueConstraint('assessment_id', 'question_order', name='uq_assessment_question_order')
    )
    
    # 3. Create indexes for assessment_questions
    op.create_index(op.f('ix_assessment_questions_id'), 'assessment_questions', ['id'], unique=False)
    op.create_index('idx_assessment_questions_assessment_id', 'assessment_questions', ['assessment_id'])
    op.create_index('idx_assessment_questions_question_id', 'assessment_questions', ['question_id'])
    op.create_index('idx_assessment_questions_order', 'assessment_questions', ['assessment_id', 'question_order'])


def downgrade() -> None:
    # Drop assessment_questions table and indexes
    op.drop_index('idx_assessment_questions_order', table_name='assessment_questions')
    op.drop_index('idx_assessment_questions_question_id', table_name='assessment_questions')
    op.drop_index('idx_assessment_questions_assessment_id', table_name='assessment_questions')
    op.drop_index(op.f('ix_assessment_questions_id'), table_name='assessment_questions')
    op.drop_table('assessment_questions')
    
    # Drop assessment indexes
    op.drop_index('idx_assessments_active_published', table_name='assessments', postgresql_where=sa.text('is_active = TRUE AND is_published = TRUE'))
    op.drop_index('idx_assessments_is_published', table_name='assessments', postgresql_where=sa.text('is_published = TRUE'))
    op.drop_index('idx_assessments_created_by', table_name='assessments')
    op.drop_index('idx_assessments_end_time', table_name='assessments')
    op.drop_index('idx_assessments_start_time', table_name='assessments')
    op.drop_index('idx_assessments_assessment_type', table_name='assessments')
    op.drop_index('idx_assessments_slug', table_name='assessments')
