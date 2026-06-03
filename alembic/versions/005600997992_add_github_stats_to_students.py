"""add_github_stats_to_students

Revision ID: 005600997992
Revises: 27ac4840a57d
Create Date: 2026-02-10 23:24:05.123456

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql


# revision identifiers, used by Alembic.
revision: str = '005600997992'
down_revision: Union[str, None] = '27ac4840a57d'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Add github_stats JSONB column
    op.add_column('students', 
        sa.Column('github_stats', 
                  postgresql.JSONB(astext_type=sa.Text()), 
                  server_default=sa.text("'{}'::jsonb"), 
                  nullable=False, 
                  comment='Cached GitHub statistics: {public_repos: 12, followers: 45, contributions: 234, stars: 56}')
    )


def downgrade() -> None:
    # Remove github_stats column
    op.drop_column('students', 'github_stats')
