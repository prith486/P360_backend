"""
Verify submission ENUMs and submissions table.
"""
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from sqlalchemy import text
from app.core.database import engine

def verify_schema():
    print("=" * 60)
    print("VERIFYING SUBMISSION ENUMS")
    print("=" * 60)
    
    with engine.connect() as conn:
        # Check ENUMs
        query = text("""
            SELECT t.typname, e.enumlabel 
            FROM pg_type t 
            JOIN pg_enum e ON t.oid = e.enumtypid  
            WHERE t.typname IN ('submission_status', 'programming_language')
            ORDER BY t.typname, e.enumsortorder
        """)
        result = conn.execute(query).fetchall()
        
        current_enum = None
        for row in result:
            if current_enum != row[0]:
                current_enum = row[0]
                print(f"\n{current_enum}:")
            print(f"  - {row[1]}")
    
    print("\n" + "=" * 60)
    print("VERIFYING SUBMISSIONS TABLE")
    print("=" * 60)
    
    with engine.connect() as conn:
        # Columns
        query = text("SELECT column_name, data_type, is_nullable FROM information_schema.columns WHERE table_name = 'submissions' AND table_schema = 'public' ORDER BY ordinal_position")
        result = conn.execute(query).fetchall()
        
        if not result:
            print("ERROR: Table 'submissions' not found!")
            return

        print(f"\nFound {len(result)} columns in 'submissions' table:")
        for row in result:
             print(f" - {row[0]}: {row[1]} (Nullable: {row[2]})")
             
        # Constraints
        constraints = conn.execute(text("SELECT conname, contype FROM pg_constraint WHERE conrelid = 'public.submissions'::regclass ORDER BY conname")).fetchall()
        print(f"\nFound {len(constraints)} constraints:")
        for row in constraints:
            constraint_type = {'c': 'CHECK', 'f': 'FOREIGN KEY', 'p': 'PRIMARY KEY', 'u': 'UNIQUE'}
            print(f" - {row[0]} ({constraint_type.get(row[1], row[1])})")

        # Indexes
        indexes = conn.execute(text("SELECT indexname FROM pg_indexes WHERE tablename = 'submissions' AND schemaname = 'public' ORDER BY indexname")).fetchall()
        print(f"\nFound {len(indexes)} indexes:")
        for row in indexes:
            print(f" - {row[0]}")

if __name__ == "__main__":
    verify_schema()
