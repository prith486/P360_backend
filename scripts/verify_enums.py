"""
Verify student profile ENUMs.
"""
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from sqlalchemy import text
from app.core.database import engine

def verify_enums():
    print("Verifying 'branch_type' and 'academic_year' ENUMs...")
    with engine.connect() as conn:
        try:
            # Check branch_type
            query = text("SELECT enumlabel FROM pg_enum WHERE enumtypid = 'branch_type'::regtype ORDER BY enumsortorder")
            res_branch = conn.execute(query).fetchall()
            print(f"Found {len(res_branch)} labels for 'branch_type':")
            for r in res_branch:
                print(f" - {r[0]}")
                
            # Check academic_year
            query = text("SELECT enumlabel FROM pg_enum WHERE enumtypid = 'academic_year'::regtype ORDER BY enumsortorder")
            res_academic = conn.execute(query).fetchall()
            print(f"\nFound {len(res_academic)} labels for 'academic_year':")
            for r in res_academic:
                print(f" - {r[0]}")
        except Exception as e:
            print(f"Error querying enums: {e}")

if __name__ == "__main__":
    verify_enums()
