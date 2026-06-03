"""create_helper_functions

Revision ID: 76c5de8d9e74
Revises: 7454807a0fb0
Create Date: 2026-02-11 00:19:21.123456

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '76c5de8d9e74'
down_revision: Union[str, None] = '7454807a0fb0'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # 1. Function to calculate student readiness score
    op.execute("""
    CREATE OR REPLACE FUNCTION calculate_readiness_score(student_id_param INTEGER)
    RETURNS NUMERIC AS $$
    DECLARE
        readiness NUMERIC;
    BEGIN
        SELECT 
            (
                -- CGPA component (30%)
                (COALESCE(s.cgpa, 0) / 10.0 * 30) +
                
                -- Problems solved component (40%)
                (LEAST(COALESCE(s.total_problems_solved, 0), 200) / 200.0 * 40) +
                
                -- Assessment performance (30%)
                (COALESCE(AVG(aa.percentage), 0) / 100.0 * 30)
            ) INTO readiness
        FROM students s
        LEFT JOIN assessment_attempts aa ON s.id = aa.student_id
        WHERE s.id = student_id_param
        GROUP BY s.id, s.cgpa, s.total_problems_solved;
        
        RETURN COALESCE(readiness, 0);
    END;
    $$ LANGUAGE plpgsql;
    """)

    # 2. Function to get assessment statistics
    op.execute("""
    CREATE OR REPLACE FUNCTION get_assessment_stats(assessment_id_param INTEGER)
    RETURNS TABLE(
        total_participants BIGINT,
        avg_score NUMERIC,
        highest_score NUMERIC,
        lowest_score NUMERIC,
        pass_percentage NUMERIC
    ) AS $$
    BEGIN
        RETURN QUERY
        SELECT 
            COUNT(DISTINCT aa.student_id),
            AVG(aa.percentage),
            MAX(aa.percentage),
            MIN(aa.percentage),
            (COUNT(*) FILTER (WHERE aa.percentage >= a.passing_score)::NUMERIC / 
             NULLIF(COUNT(*), 0) * 100)
        FROM assessment_attempts aa
        JOIN assessments a ON aa.assessment_id = a.id
        WHERE aa.assessment_id = assessment_id_param
          AND aa.submitted_at IS NOT NULL;
    END;
    $$ LANGUAGE plpgsql;
    """)


def downgrade() -> None:
    op.execute("DROP FUNCTION IF EXISTS get_assessment_stats(INTEGER)")
    op.execute("DROP FUNCTION IF EXISTS calculate_readiness_score(INTEGER)")
