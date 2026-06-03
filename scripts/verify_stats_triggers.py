"""
Verify stats triggers.
"""
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from sqlalchemy import text
from app.core.database import engine

def verify_triggers():
    print("=" * 60)
    print("VERIFYING STATISTICS TRIGGERS")
    print("=" * 60)
    
    with engine.connect() as conn:
        query = text("""
            SELECT tgname, tgrelid::regclass, tgtype 
            FROM pg_trigger 
            WHERE tgisinternal = FALSE;
        """)
        result = conn.execute(query).fetchall()
        
        print(f"\nFound {len(result)} non-internal triggers:")
        for row in result:
            print(f" - {row[0]} on {row[1]}")

        # Check for trigger functions specifically
        print("\nChecking trigger functions...")
        func_query = text("""
            SELECT proname 
            FROM pg_proc 
            WHERE proname IN ('update_student_stats', 'update_assessment_stats');
        """)
        funcs = conn.execute(func_query).fetchall()
        for f in funcs:
            print(f" - Found function: {f[0]}")

if __name__ == "__main__":
    verify_triggers()
