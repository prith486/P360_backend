from app.core.database import SessionLocal
from sqlalchemy import text

db = SessionLocal()

try:
    # Check if any job-related tables exist
    result = db.execute(text("""
        SELECT table_name 
        FROM information_schema.tables 
        WHERE table_schema = 'public' 
        AND table_name IN (
            'jobs', 'job_postings', 'companies', 'applications', 
            'job_applications', 'placements', 'placement_drives'
        )
        ORDER BY table_name
    """))
    print("=== EXISTING JOB-RELATED TABLES ===")
    tab_count = 0
    for row in result:
        print(f"  {row[0]}")
        tab_count += 1
    if tab_count == 0:
        print("  (None found)")

    # Check students table for placement-related columns
    result2 = db.execute(text("""
        SELECT column_name, data_type 
        FROM information_schema.columns 
        WHERE table_name = 'students' 
        AND column_name IN (
            'is_placement_ready', 'expected_ctc_min', 'expected_ctc_max',
            'willing_to_relocate', 'preferred_roles', 'skills',
            'resume_url', 'linkedin_url', 'cgpa', 'readiness_score'
        )
        ORDER BY column_name
    """))
    print("\n=== STUDENT PLACEMENT COLUMNS ===")
    col_count = 0
    for row in result2:
        print(f"  {row[0]}: {row[1]}")
        col_count += 1
    if col_count == 0:
        print("  (None found)")

finally:
    db.close()
