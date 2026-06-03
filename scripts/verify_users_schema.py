"""
Verify Users table schema.
"""
from sqlalchemy import text
import sys
import os

# Add the project root to Python path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.core.database import engine

def verify_table():
    print("Verifying 'public.users' table schema...")
    with engine.connect() as conn:
        query = text("SELECT column_name, data_type, is_nullable FROM information_schema.columns WHERE table_name = 'users' AND table_schema = 'public' ORDER BY ordinal_position")
        result = conn.execute(query).fetchall()
        
        if not result:
            print("ERROR: Table 'users' not found!")
            return

        print(f"Found {len(result)} columns in 'users' table:")
        for row in result:
             print(f" - {row[0]}: {row[1]} (Nullable: {row[2]})")
             
        # Check constraints (simple check)
        constraints = conn.execute(text("SELECT conname, contype FROM pg_constraint WHERE conrelid = 'public.users'::regclass")).fetchall()
        print(f"\nFound {len(constraints)} constraints:")
        for row in constraints:
            print(f" - {row[0]} ({row[1]})")

        # Check indexes
        indexes = conn.execute(text("SELECT indexname, indexdef FROM pg_indexes WHERE tablename = 'users' AND schemaname = 'public'")).fetchall()
        print(f"\nFound {len(indexes)} indexes:")
        for row in indexes:
            print(f" - {row[0]}")

if __name__ == "__main__":
    verify_table()
