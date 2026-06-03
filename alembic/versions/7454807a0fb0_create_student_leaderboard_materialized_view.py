"""create_student_leaderboard_materialized_view

Revision ID: 7454807a0fb0
Revises: d4521ae20bf4
Create Date: 2026-02-11 00:06:32.123456

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '7454807a0fb0'
down_revision: Union[str, None] = 'd4521ae20bf4'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Create materialized view for student leaderboard
    op.execute("""
        CREATE MATERIALIZED VIEW student_leaderboard AS
        SELECT 
            s.id AS student_id,
            s.roll_number,
            s.batch_year,
            s.branch,
            s.current_year,
            s.cgpa,
            s.readiness_score,
            s.total_problems_solved,
            s.current_streak_days,
            u.full_name,
            
            -- Calculate rank within branch and year
            RANK() OVER (
                PARTITION BY s.batch_year, s.branch 
                ORDER BY s.readiness_score DESC, s.total_problems_solved DESC
            ) AS branch_rank,
            
            -- Calculate overall rank
            RANK() OVER (
                ORDER BY s.readiness_score DESC, s.total_problems_solved DESC
            ) AS overall_rank,
            
            -- Count submissions
            COUNT(DISTINCT sub.id) AS total_submissions,
            COUNT(DISTINCT CASE WHEN sub.status = 'accepted' THEN sub.question_id END) AS unique_problems_solved,
            
            -- Average score
            AVG(CASE WHEN sub.status = 'accepted' THEN sub.score END) AS avg_submission_score
            
        FROM students s
        JOIN users u ON s.user_id = u.id
        LEFT JOIN submissions sub ON s.id = sub.student_id
        WHERE u.status = 'active'
        GROUP BY s.id, s.roll_number, s.batch_year, s.branch, s.current_year, 
                 s.cgpa, s.readiness_score, s.total_problems_solved, 
                 s.current_streak_days, u.full_name;
    """)
    
    # Create indexes on materialized view
    op.create_index('idx_leaderboard_branch_rank', 'student_leaderboard', ['branch', 'branch_rank'])
    op.create_index('idx_leaderboard_overall_rank', 'student_leaderboard', ['overall_rank'])
    op.create_index('idx_leaderboard_readiness', 'student_leaderboard', [sa.text('readiness_score DESC')])
    
    # Create unique index on student_id to enable CONCURRENT refresh
    op.create_index('idx_leaderboard_student_id', 'student_leaderboard', ['student_id'], unique=True)


def downgrade() -> None:
    # Drop indexes
    op.drop_index('idx_leaderboard_student_id', table_name='student_leaderboard')
    op.drop_index('idx_leaderboard_readiness', table_name='student_leaderboard')
    op.drop_index('idx_leaderboard_overall_rank', table_name='student_leaderboard')
    op.drop_index('idx_leaderboard_branch_rank', table_name='student_leaderboard')
    
    # Drop materialized view
    op.execute("DROP MATERIALIZED VIEW IF EXISTS student_leaderboard")
