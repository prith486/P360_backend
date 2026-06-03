"""create_stats_triggers

Revision ID: 306b0ba4be7e
Revises: 76c5de8d9e74
Create Date: 2026-02-11 00:22:10.123456

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '306b0ba4be7e'
down_revision: Union[str, None] = '76c5de8d9e74'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # 1. Trigger function for student stats
    op.execute("""
    CREATE OR REPLACE FUNCTION update_student_stats()
    RETURNS TRIGGER AS $$
    BEGIN
        -- Update total problems solved
        UPDATE students
        SET 
            total_problems_solved = (
                SELECT COUNT(DISTINCT question_id)
                FROM submissions
                WHERE student_id = NEW.student_id
                  AND status = 'accepted'
            ),
            updated_at = NOW()
        WHERE id = NEW.student_id;
        
        RETURN NEW;
    END;
    $$ LANGUAGE plpgsql;
    """)

    # 2. Trigger on submissions
    op.execute("""
    CREATE TRIGGER trigger_update_student_stats
    AFTER INSERT OR UPDATE ON submissions
    FOR EACH ROW
    WHEN (NEW.status = 'accepted')
    EXECUTE FUNCTION update_student_stats();
    """)

    # 3. Trigger function for assessment stats
    op.execute("""
    CREATE OR REPLACE FUNCTION update_assessment_stats()
    RETURNS TRIGGER AS $$
    BEGIN
        UPDATE assessments
        SET 
            total_participants = (
                SELECT COUNT(DISTINCT student_id)
                FROM assessment_attempts
                WHERE assessment_id = NEW.assessment_id
            ),
            average_score = (
                SELECT AVG(percentage)
                FROM assessment_attempts
                WHERE assessment_id = NEW.assessment_id
                  AND submitted_at IS NOT NULL
            ),
            updated_at = NOW()
        WHERE id = NEW.assessment_id;
        
        RETURN NEW;
    END;
    $$ LANGUAGE plpgsql;
    """)

    # 4. Trigger on assessment_attempts
    op.execute("""
    CREATE TRIGGER trigger_update_assessment_stats
    AFTER INSERT OR UPDATE ON assessment_attempts
    FOR EACH ROW
    WHEN (NEW.submitted_at IS NOT NULL)
    EXECUTE FUNCTION update_assessment_stats();
    """)


def downgrade() -> None:
    # Drop triggers
    op.execute("DROP TRIGGER IF EXISTS trigger_update_assessment_stats ON assessment_attempts")
    op.execute("DROP TRIGGER IF EXISTS trigger_update_student_stats ON submissions")
    
    # Drop functions
    op.execute("DROP FUNCTION IF EXISTS update_assessment_stats()")
    op.execute("DROP FUNCTION IF EXISTS update_student_stats()")
