"""
Verify submissions table indexes.
"""
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from sqlalchemy import text
from app.core.database import engine

def verify_indexes():
    print("=" * 60)
    print("VERIFYING SUBMISSIONS INDEXES")
    print("=" * 60)
    
    with engine.connect() as conn:
        # Check submissions indexes
        indexes = conn.execute(text("SELECT indexname FROM pg_indexes WHERE tablename = 'submissions' AND schemaname = 'public' ORDER BY indexname")).fetchall()
        print(f"\nFound {len(indexes)} indexes on 'submissions' table:")
        for row in indexes:
            print(f" - {row[0]}")

if __name__ == "__main__":
    verify_indexes()
