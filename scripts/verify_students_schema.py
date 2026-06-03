"""
Verify Students table schema.
"""
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from sqlalchemy import text
from app.core.database import engine

def verify_table():
    print("Verifying 'public.students' table schema...")
    with engine.connect() as conn:
        query = text("SELECT column_name, data_type, is_nullable FROM information_schema.columns WHERE table_name = 'students' AND table_schema = 'public' ORDER BY ordinal_position")
        result = conn.execute(query).fetchall()
        
        if not result:
            print("ERROR: Table 'students' not found!")
            return

        print(f"Found {len(result)} columns in 'students' table:")
        for row in result:
             # print type
             dtype = row[1]
             nullable = row[2]
             print(f" - {row[0]}: {dtype} (Nullable: {nullable})")
             
        # Check constraints
        constraints = conn.execute(text("SELECT conname, contype FROM pg_constraint WHERE conrelid = 'public.students'::regclass")).fetchall()
        print(f"\nFound {len(constraints)} constraints:")
        for row in constraints:
            print(f" - {row[0]} ({row[1]})")

        # Check indexes
        indexes = conn.execute(text("SELECT indexname, indexdef FROM pg_indexes WHERE tablename = 'students' AND schemaname = 'public'")).fetchall()
        print(f"\nFound {len(indexes)} indexes:")
        for row in indexes:
            print(f" - {row[0]}")

if __name__ == "__main__":
    verify_table()
