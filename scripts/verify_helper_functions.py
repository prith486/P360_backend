"""
Verify helper functions calculate_readiness_score and get_assessment_stats.
"""
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from sqlalchemy import text
from app.core.database import engine

def verify_functions():
    print("=" * 60)
    print("VERIFYING HELPER FUNCTIONS")
    print("=" * 60)
    
    with engine.connect() as conn:
        # Test readiness score calculation (ID 1 as a dummy)
        print("\nTesting calculate_readiness_score(1)...")
        try:
            result = conn.execute(text("SELECT calculate_readiness_score(1)")).scalar()
            print(f"Result: {result}")
        except Exception as e:
            print(f"Error: {e}")

        # Test assessment stats calculation (ID 1 as a dummy)
        print("\nTesting get_assessment_stats(1)...")
        try:
            result = conn.execute(text("SELECT * FROM get_assessment_stats(1)")).fetchall()
            print(f"Result row count: {len(result)}")
            if result:
                 print(f"Data: {result[0]}")
        except Exception as e:
            print(f"Error: {e}")

if __name__ == "__main__":
    verify_functions()
