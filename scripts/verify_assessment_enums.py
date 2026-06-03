"""
Verify Assessment, Question, and Difficulty ENUMs.
"""
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from sqlalchemy import text
from app.core.database import engine

def verify_enums():
    print("Verifying 'difficulty_level', 'question_type', and 'assessment_type' ENUMs...")
    with engine.connect() as conn:
        try:
            # Check difficulty_level
            query = text("SELECT enumlabel FROM pg_enum WHERE enumtypid = 'difficulty_level'::regtype ORDER BY enumsortorder")
            res_diff = conn.execute(query).fetchall()
            print(f"Found {len(res_diff)} labels for 'difficulty_level':")
            for r in res_diff:
                print(f" - {r[0]}")
                
            # Check question_type
            query = text("SELECT enumlabel FROM pg_enum WHERE enumtypid = 'question_type'::regtype ORDER BY enumsortorder")
            res_quest = conn.execute(query).fetchall()
            print(f"\nFound {len(res_quest)} labels for 'question_type':")
            for r in res_quest:
                print(f" - {r[0]}")

            # Check assessment_type
            query = text("SELECT enumlabel FROM pg_enum WHERE enumtypid = 'assessment_type'::regtype ORDER BY enumsortorder")
            res_assess = conn.execute(query).fetchall()
            print(f"\nFound {len(res_assess)} labels for 'assessment_type':")
            for r in res_assess:
                print(f" - {r[0]}")

        except Exception as e:
            print(f"Error querying enums: {e}")

if __name__ == "__main__":
    verify_enums()
