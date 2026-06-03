"""
Verify composite indexes using EXPLAIN ANALYZE and check for Index Scan.
"""
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from sqlalchemy import text
from app.core.database import engine

def verify_performance():
    queries = [
        {
            "name": "Student Leaderboard Query",
            "sql": "EXPLAIN SELECT * FROM students WHERE branch = 'computer_science' AND current_year = 'fourth' ORDER BY readiness_score DESC LIMIT 20;"
        },
        {
            "name": "Question Bank Query",
            "sql": "EXPLAIN SELECT id FROM questions WHERE difficulty = 'medium' AND question_type = 'coding' AND is_active = TRUE AND is_public = TRUE;"
        },
        {
            "name": "Submission History Query",
            "sql": "EXPLAIN SELECT question_id, score FROM submissions WHERE student_id = 1 ORDER BY submitted_at DESC LIMIT 10;"
        }
    ]
    
    with engine.connect() as conn:
        for q in queries:
            print(f"Checking {q['name']}...")
            result = conn.execute(text(q['sql'])).fetchall()
            plan = "\n".join([row[0] for row in result])
            if "Index Scan" in plan or "Index Only Scan" in plan or "Bitmap Index Scan" in plan:
                print(f"  [SUCCESS] Use index: Yes")
                # Print the first line for confirmation
                print(f"  [PLAN]: {result[0][0]}")
            else:
                print(f"  [FAILURE] Use index: No (Sequential Scan detected)")
                print(f"  [PLAN]: {plan}")
            print("-" * 40)

if __name__ == "__main__":
    verify_performance()
