"""create_student_enums (updated)

Revision ID: 0e5f3cd85f6f
Revises: 4c05c11a6b66
Create Date: 2026-02-10 22:51:19.497042

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy.dialects.postgresql as pg


# revision identifiers, used by Alembic.
revision: str = '0e5f3cd85f6f'
down_revision: Union[str, None] = '4c05c11a6b66'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # 1. branch_type (Modified: removed mechanical/civil/chemical/other, added ai_ml)
    # The user asked: 'computer_science', 'information_technology', 'electronics', 'electrical', 'ai_ml'
    # Use create_type=False because we call create explicitly
    branch_type = pg.ENUM(
        'computer_science', 'information_technology', 'electronics', 
        'electrical', 'ai_ml',
        name='branch_type',
        create_type=False
    )
    branch_type.create(op.get_bind(), checkfirst=True)
    
    # 2. academic_year (Modified: removed passout)
    # The user asked: 'first', 'second', 'third', 'fourth'
    academic_year = pg.ENUM(
        'first', 'second', 'third', 'fourth',
        name='academic_year',
        create_type=False
    )
    academic_year.create(op.get_bind(), checkfirst=True)


def downgrade() -> None:
    # Drop types
    op.execute("DROP TYPE IF EXISTS branch_type")
    op.execute("DROP TYPE IF EXISTS academic_year")
