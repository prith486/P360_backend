import sys
sys.stdout = open('output_utf8.txt', 'w', encoding='utf-8')

import requests
from app.core.database import SessionLocal
from sqlalchemy import text

db = SessionLocal()

# 1. Students table columns
result = db.execute(text("""
    SELECT column_name, data_type 
    FROM information_schema.columns 
    WHERE table_name = 'students' 
    ORDER BY ordinal_position
"""))
print("=== STUDENTS TABLE ===")
for row in result:
    print(f"  {row[0]}: {row[1]}")

# 2. Assessment attempts table columns
result2 = db.execute(text("""
    SELECT column_name, data_type 
    FROM information_schema.columns 
    WHERE table_name = 'assessment_attempts' 
    ORDER BY ordinal_position
"""))
print("\n=== ASSESSMENT_ATTEMPTS TABLE ===")
for row in result2:
    print(f"  {row[0]}: {row[1]}")

# 3. Assessments table columns
result3 = db.execute(text("""
    SELECT column_name, data_type 
    FROM information_schema.columns 
    WHERE table_name = 'assessments' 
    ORDER BY ordinal_position
"""))
print("\n=== ASSESSMENTS TABLE ===")
for row in result3:
    print(f"  {row[0]}: {row[1]}")

# 4. Sample student data to see current readiness_score values
result4 = db.execute(text("""
    SELECT user_id, roll_number, cgpa, readiness_score, 
           total_problems_solved, profile_completion_percent,
           leetcode_stats IS NOT NULL as has_lc,
           github_stats IS NOT NULL as has_gh
    FROM students
    LIMIT 7
"""))
print("\n=== SAMPLE STUDENTS ===")
for row in result4:
    print(f"  {row[0]} {row[1]}: cgpa={row[2]}, readiness={row[3]}, problems={row[4]}, completion={row[5]}, has_lc={row[6]}, has_gh={row[7]}")

# 5. Sample assessment attempts
result5 = db.execute(text("""
    SELECT s.user_id, aa.total_score, aa.max_score, aa.is_submitted, aa.submitted_at
    FROM assessment_attempts aa
    JOIN students s ON aa.student_id = s.id
    WHERE aa.is_submitted = true
    LIMIT 10
"""))
print("\n=== SAMPLE ATTEMPTS ===")
for row in result5:
    print(f"  {row[0]}: score={row[1]}/{row[2]}, submitted={row[4]}")

db.close()
sys.stdout.close()
