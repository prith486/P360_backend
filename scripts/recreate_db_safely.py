import os
import sys
import logging
from sqlalchemy import text

# Add current directory to path
sys.path.append(os.getcwd())

from app.core.database import engine, Base
# Import all models to ensure Base knows about them
from app.models import (
    auth_user, student, faculty, question, assessment, 
    assessment_question, submission, assessment_attempt, admin_activity
)

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("recreate_db")

def recreate():
    try:
        with engine.connect() as conn:
            logger.info("Dropping public schema objects...")
            # Drop views and tables in public schema only
            conn.execute(text("DROP MATERIALIZED VIEW IF EXISTS student_leaderboard CASCADE"))
            
            # Get list of all tables in public schema
            res = conn.execute(text("SELECT tablename FROM pg_tables WHERE schemaname = 'public'"))
            tables = [row[0] for row in res]
            
            for table in tables:
                logger.info(f"Dropping table {table}...")
                conn.execute(text(f"DROP TABLE IF EXISTS {table} CASCADE"))
            
            conn.commit()
            logger.info("✓ Public schema cleared")

        # Recreate tables from SQLAlchemy models
        logger.info("Recreating tables from models...")
        Base.metadata.create_all(bind=engine)
        logger.info("✓ Tables recreated")

        # Manually recreate materialized view (since it's not in Base.metadata typically)
        with engine.connect() as conn:
            logger.info("Recreating materialized view student_leaderboard...")
            conn.execute(text("""
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
                    COALESCE(u.raw_user_meta_data->>'full_name', u.email) AS full_name,
                    RANK() OVER (PARTITION BY s.batch_year, s.branch ORDER BY s.readiness_score DESC) AS branch_rank,
                    RANK() OVER (ORDER BY s.readiness_score DESC) AS overall_rank
                FROM students s
                JOIN auth.users u ON s.user_id = u.id;
            """))
            conn.execute(text("CREATE UNIQUE INDEX idx_leaderboard_student_id ON student_leaderboard (student_id)"))
            conn.commit()
            logger.info("✓ Materialized view created")

    except Exception as e:
        logger.error(f"Error during recreation: {e}")
        sys.exit(1)
    finally:
        engine.dispose()

if __name__ == "__main__":
    recreate()
