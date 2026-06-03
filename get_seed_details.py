import os
import uuid
import base64
import json
from sqlalchemy import create_engine, text
from dotenv import load_dotenv

load_dotenv('c:\\Users\\PRIHTVIRAJ\\Desktop\\P360_BACKEND\\placement360-backend\\.env')
db_url = os.getenv('DATABASE_URL')
engine = create_engine(db_url)

def get_seeded_info():
    with engine.connect() as conn:
        print("--- SEEDED STUDENT ---")
        student = conn.execute(text("SELECT id, user_id, roll_number, branch FROM students LIMIT 1")).fetchone()
        if student:
            print(f"id: {student.id}")
            print(f"user_id: {student.user_id}")
            print(f"roll_number: {student.roll_number}")
            print(f"branch: {student.branch}")
            
            # Check auth.users for name/email
            user = conn.execute(text("SELECT email, raw_user_meta_data FROM auth.users WHERE id = :uid"), {"uid": student.user_id}).fetchone()
            if user:
                print(f"email: {user.email}")
                print(f"meta: {user.raw_user_meta_data}")
        else:
            print("No student found")

        print("\n--- SEEDED FACULTY ---")
        faculty = conn.execute(text("SELECT id, user_id, employee_id, department FROM faculty LIMIT 1")).fetchone()
        if faculty:
            print(f"id: {faculty.id}")
            print(f"user_id: {faculty.user_id}")
            print(f"employee_id: {faculty.employee_id}")
            print(f"department: {faculty.department}")
            
            # Check auth.users for name/email
            user = conn.execute(text("SELECT email, raw_user_meta_data FROM auth.users WHERE id = :uid"), {"uid": faculty.user_id}).fetchone()
            if user:
                print(f"email: {user.email}")
                print(f"meta: {user.raw_user_meta_data}")
        else:
            print("No faculty found")

if __name__ == "__main__":
    get_seeded_info()
