import uuid
from sqlalchemy import text
from app.core.database import SessionLocal
from app.models.student import Student
from app.models.faculty import Faculty
from app.models.enums import BranchType, AcademicYear

def seed():
    db = SessionLocal()
    try:
        # Pre-seed check: Ensure 'section' column exists to avoid crash
        try:
            db.execute(text("ALTER TABLE students ADD COLUMN IF NOT EXISTS section VARCHAR(10)"))
            db.commit()
        except Exception as e:
            print(f"Warning: Could not add 'section' column (may already exist or no permission): {e}")
            db.rollback()

        # 1. Create Mock Student if not exists
        student_user_id = uuid.UUID("00000000-0000-0000-0000-000000000001")
        
        # We need to bypass the ForeignKey to auth.users if it doesn't exist locally
        # Or just create it in the 'users' table if it resides in public schema (it shouldn't)
        # But for mock purposes, let's just use raw SQL to insert into students ignoring FK if possible
        # or better: check if we can insert into auth.users
        
        try:
            db.execute(text("INSERT INTO auth.users (id, email, raw_user_meta_data) VALUES (:id, :email, :meta) ON CONFLICT (id) DO NOTHING"), 
                       {"id": student_user_id, "email": "test@student.com", "meta": '{"full_name": "Test Student"}'})
        except Exception as e:
            print(f"Bypassing auth.users insert (likely no 'auth' schema locally): {e}")

        # Ensure student exists
        student_exists = db.execute(text("SELECT id FROM students WHERE user_id = :id"), {"id": student_user_id}).first()
        if not student_exists:
            db.execute(text("""
                INSERT INTO students 
                (id, user_id, roll_number, branch, batch_year, current_year, readiness_score, total_problems_solved, profile_completion_percent, total_backlogs, active_backlogs) 
                VALUES 
                (:id, :user_id, :roll, CAST(:branch AS branch_type), :batch, CAST(:year AS academic_year), :score, :solved, :completion, 0, 0)
            """), {
                "id": uuid.uuid4(),
                "user_id": student_user_id,
                "roll": "MOCK001",
                "branch": "computer_science",
                "batch": 2021,
                "year": "third",
                "score": 75,
                "solved": 42,
                "completion": 85
            })
            print("Created mock student record.")
        else:
            print("Mock student record already exists.")

        # 2. Create Mock Faculty if not exists
        faculty_user_id = uuid.UUID("00000000-0000-0000-0000-000000000002")
        try:
            db.execute(text("INSERT INTO auth.users (id, email, raw_user_meta_data) VALUES (:id, :email, :meta) ON CONFLICT (id) DO NOTHING"), 
                       {"id": faculty_user_id, "email": "test@faculty.com", "meta": '{"full_name": "Test Faculty"}'})
        except:
             pass

        faculty = db.query(Faculty).filter(Faculty.user_id == faculty_user_id).first()
        if not faculty:
            faculty = Faculty(
                user_id=faculty_user_id,
                employee_id="EMP001",
                department="Computer Science",
                designation="Senior Professor"
            )
            db.add(faculty)
            print("Created mock faculty record.")
        else:
            print("Mock faculty record already exists.")

        db.commit()
    except Exception as e:
        print(f"Error seeding: {e}")
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    seed()
