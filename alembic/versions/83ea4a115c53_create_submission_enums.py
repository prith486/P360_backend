"""create_submission_enums

Revision ID: 83ea4a115c53
Revises: b9f6c80e2a85
Create Date: 2026-02-10 23:51:26.123456

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql as pg


# revision identifiers, used by Alembic.
revision: str = '83ea4a115c53'
down_revision: Union[str, None] = 'b9f6c80e2a85'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # 1. submission_status ENUM
    submission_status = pg.ENUM(
        'pending', 'running', 'accepted', 'wrong_answer', 
        'time_limit', 'memory_limit', 'runtime_error', 
        'compile_error', 'internal_error',
        name='submission_status'
    )
    submission_status.create(op.get_bind(), checkfirst=True)

    # 2. programming_language ENUM
    programming_language = pg.ENUM(
        'python', 'cpp', 'java', 'javascript', 'c', 
        'csharp', 'ruby', 'go', 'rust', 'kotlin', 'swift',
        name='programming_language'
    )
    programming_language.create(op.get_bind(), checkfirst=True)


def downgrade() -> None:
    op.execute("DROP TYPE IF EXISTS programming_language")
    op.execute("DROP TYPE IF EXISTS submission_status")
