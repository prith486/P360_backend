"""add_missing_platform_gin_indexes

Revision ID: 7741a795a262
Revises: 005600997992
Create Date: 2026-02-10 23:25:52.123456

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '7741a795a262'
down_revision: Union[str, None] = '005600997992'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Add GIN indexes for the remaining platform stats JSONB columns
    op.create_index('idx_students_codeforces_stats', 'students', ['codeforces_stats'], postgresql_using='gin')
    op.create_index('idx_students_codechef_stats', 'students', ['codechef_stats'], postgresql_using='gin')
    op.create_index('idx_students_geeksforgeeks_stats', 'students', ['geeksforgeeks_stats'], postgresql_using='gin')
    op.create_index('idx_students_hackerrank_stats', 'students', ['hackerrank_stats'], postgresql_using='gin')
    op.create_index('idx_students_github_stats', 'students', ['github_stats'], postgresql_using='gin')


def downgrade() -> None:
    op.drop_index('idx_students_github_stats', table_name='students')
    op.drop_index('idx_students_hackerrank_stats', table_name='students')
    op.drop_index('idx_students_geeksforgeeks_stats', table_name='students')
    op.drop_index('idx_students_codechef_stats', table_name='students')
    op.drop_index('idx_students_codeforces_stats', table_name='students')
