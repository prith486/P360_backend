"""
Verify Assessment indexes and AssessmentQuestion mapping table.
"""
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from sqlalchemy import text
from app.core.database import engine

def verify_schema():
    print("=" * 60)
    print("VERIFYING ASSESSMENTS INDEXES")
    print("=" * 60)
    
    with engine.connect() as conn:
        # Check assessments indexes
        indexes = conn.execute(text("SELECT indexname FROM pg_indexes WHERE tablename = 'assessments' AND schemaname = 'public' ORDER BY indexname")).fetchall()
        print(f"\nFound {len(indexes)} indexes on 'assessments' table:")
        for row in indexes:
            print(f" - {row[0]}")
    
    print("\n" + "=" * 60)
    print("VERIFYING ASSESSMENT_QUESTIONS TABLE")
    print("=" * 60)
    
    with engine.connect() as conn:
        # Columns
        query = text("SELECT column_name, data_type, is_nullable FROM information_schema.columns WHERE table_name = 'assessment_questions' AND table_schema = 'public' ORDER BY ordinal_position")
        result = conn.execute(query).fetchall()
        
        if not result:
            print("ERROR: Table 'assessment_questions' not found!")
            return

        print(f"\nFound {len(result)} columns in 'assessment_questions' table:")
        for row in result:
             print(f" - {row[0]}: {row[1]} (Nullable: {row[2]})")
             
        # Constraints
        constraints = conn.execute(text("SELECT conname, contype FROM pg_constraint WHERE conrelid = 'public.assessment_questions'::regclass ORDER BY conname")).fetchall()
        print(f"\nFound {len(constraints)} constraints:")
        for row in constraints:
            print(f" - {row[0]} ({row[1]})")

        # Indexes
        indexes = conn.execute(text("SELECT indexname FROM pg_indexes WHERE tablename = 'assessment_questions' AND schemaname = 'public' ORDER BY indexname")).fetchall()
        print(f"\nFound {len(indexes)} indexes:")
        for row in indexes:
            print(f" - {row[0]}")

if __name__ == "__main__":
    verify_schema()
