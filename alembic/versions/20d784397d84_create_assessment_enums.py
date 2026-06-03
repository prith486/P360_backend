"""create_assessment_enums

Revision ID: 20d784397d84
Revises: 6b0dbf7dc97b
Create Date: 2026-02-10 23:38:23.123456

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql as pg


# revision identifiers, used by Alembic.
revision: str = '20d784397d84'
down_revision: Union[str, None] = '6b0dbf7dc97b'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # 1. difficulty_level
    difficulty_level = pg.ENUM('easy', 'medium', 'hard', name='difficulty_level')
    difficulty_level.create(op.get_bind(), checkfirst=True)

    # 2. question_type
    question_type = pg.ENUM('coding', 'mcq', 'fill_in_blank', 'sql', 'debugging', name='question_type')
    question_type.create(op.get_bind(), checkfirst=True)

    # 3. assessment_type
    assessment_type = pg.ENUM('practice', 'mock_test', 'placement_test', 'assignment', name='assessment_type')
    assessment_type.create(op.get_bind(), checkfirst=True)


def downgrade() -> None:
    op.execute("DROP TYPE IF EXISTS assessment_type")
    op.execute("DROP TYPE IF EXISTS question_type")
    op.execute("DROP TYPE IF EXISTS difficulty_level")
