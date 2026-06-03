"""
Verify student_leaderboard materialized view and its indexes.
"""
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from sqlalchemy import text
from app.core.database import engine

def verify_materialized_view():
    print("=" * 60)
    print("VERIFYING STUDENT_LEADERBOARD MATERIALIZED VIEW")
    print("=" * 60)
    
    with engine.connect() as conn:
        # 1. Check if the view exists and list columns
        print("\nChecking columns...")
        query = text("""
            SELECT column_name, data_type 
            FROM information_schema.columns 
            WHERE table_name = 'student_leaderboard'
        """)
        result = conn.execute(query).fetchall()
        if not result:
            # information_schema.columns doesn't always show materialized views in some PG versions
            # let's try a different system catalog table
            query = text("""
                SELECT a.attname AS column_name, t.typname AS data_type
                FROM pg_attribute a
                JOIN pg_class c ON a.attrelid = c.oid
                JOIN pg_type t ON a.atttypid = t.oid
                WHERE c.relname = 'student_leaderboard' AND a.attnum > 0;
            """)
            result = conn.execute(query).fetchall()

        for row in result:
            print(f" - {row[0]}: {row[1]}")

        # 2. Check indexes
        print("\nChecking indexes...")
        query = text("""
            SELECT indexname, indexdef 
            FROM pg_indexes 
            WHERE tablename = 'student_leaderboard'
        """)
        indexes = conn.execute(query).fetchall()
        for idx in indexes:
            print(f" - {idx[0]}")

        # 3. Test query (Expected to be empty but should not error)
        print("\nTesting data retrieval (Top 10 overall)...")
        query = text("""
            SELECT roll_number, full_name, branch, overall_rank, branch_rank, readiness_score
            FROM student_leaderboard
            ORDER BY overall_rank
            LIMIT 10;
        """)
        try:
            data = conn.execute(query).fetchall()
            if not data:
                print("No data found (expected if no students are in the DB yet).")
            for row in data:
                print(row)
        except Exception as e:
            print(f"Error querying view: {e}")

if __name__ == "__main__":
    verify_materialized_view()
