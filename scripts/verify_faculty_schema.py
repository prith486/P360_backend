"""
Verify Faculty table schema.
"""
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from sqlalchemy import text
from app.core.database import engine

def verify_table():
    print("Verifying 'public.faculty' table schema...")
    with engine.connect() as conn:
        # Columns
        query = text("SELECT column_name, data_type, is_nullable FROM information_schema.columns WHERE table_name = 'faculty' AND table_schema = 'public' ORDER BY ordinal_position")
        result = conn.execute(query).fetchall()
        
        if not result:
            print("ERROR: Table 'faculty' not found!")
            return

        print(f"Found {len(result)} columns in 'faculty' table:")
        for row in result:
             print(f" - {row[0]}: {row[1]} (Nullable: {row[2]})")
             
        # Constraints
        constraints = conn.execute(text("SELECT conname, contype FROM pg_constraint WHERE conrelid = 'public.faculty'::regclass")).fetchall()
        print(f"\nFound {len(constraints)} constraints:")
        for row in constraints:
            print(f" - {row[0]} ({row[1]})")

        # Indexes
        indexes = conn.execute(text("SELECT indexname, indexdef FROM pg_indexes WHERE tablename = 'faculty' AND schemaname = 'public'")).fetchall()
        print(f"\nFound {len(indexes)} indexes:")
        for row in indexes:
            print(f" - {row[0]}")

if __name__ == "__main__":
    verify_table()
