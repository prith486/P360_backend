import os, requests, sys
from dotenv import load_dotenv

# Add project root to path for imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.core.config import settings
from app.core.database import get_session_local
from app.models.student import Student
from app.models.faculty import Faculty

# Use absolute path to .env
env_path = r"c:\Users\PRIHTVIRAJ\Desktop\P360_BACKEND\placement360-backend\.env"
load_dotenv(dotenv_path=env_path)

SUPABASE_URL = os.getenv("SUPABASE_URL")
SERVICE_KEY = os.getenv("SUPABASE_SERVICE_ROLE_KEY")

headers = {
    "apikey": SERVICE_KEY,
    "Authorization": f"Bearer {SERVICE_KEY}",
    "Content-Type": "application/json"
}

students = [
    {"full_name": "Aarav Sharma", "email": "aarav@placement360.dev", "password": "Student@123", "roll": "CS21B001", "branch": "computer_science", "year": "fourth"},
    {"full_name": "Priya Patel", "email": "priya.p@placement360.dev", "password": "Student@123", "roll": "CS21B002", "branch": "computer_science", "year": "fourth"},
    {"full_name": "Rahul Verma", "email": "rahul@placement360.dev", "password": "Student@123", "roll": "IT21B001", "branch": "information_technology", "year": "fourth"},
    {"full_name": "Sneha Reddy", "email": "sneha@placement360.dev", "password": "Student@123", "roll": "CS22B001", "branch": "computer_science", "year": "third"},
    {"full_name": "Arjun Singh", "email": "arjun@placement360.dev", "password": "Student@123", "roll": "CS21B003", "branch": "computer_science", "year": "fourth"},
]

faculties = [
    {"full_name": "Dr. Priya Sharma (Test)", "email": "drpriya@placement360.dev", "password": "Faculty@123", "emp_id": "FAC2021005", "dept": "computer_science"},
    {"full_name": "Prof. Ravi Kumar", "email": "ravi@placement360.dev", "password": "Faculty@123", "emp_id": "FAC2021002", "dept": "information_technology"},
]

def seed():
    SessionLocal = get_session_local()
    db = SessionLocal()
    
    # 1. Seed Students
    print("--- Seeding Students ---")
    for s in students:
        # Create in Auth
        res = requests.post(f"{SUPABASE_URL}/auth/v1/admin/users", headers=headers, json={
            "email": s["email"], "password": s["password"], "email_confirm": True,
            "user_metadata": {"full_name": s["full_name"], "role": "student"}
        })
        user_id = None
        if res.status_code in [200, 201]: user_id = res.json()["id"]; print(f"Auth created: {s['email']}")
        else:
            res_list = requests.get(f"{SUPABASE_URL}/auth/v1/admin/users", headers=headers)
            for u in res_list.json().get('users', []):
                if u['email'] == s['email']: user_id = u['id']; break
            print(f"Auth existing/checked: {s['email']}")

        if user_id:
            existing = db.query(Student).filter(Student.user_id == user_id).first()
            if not existing:
                # Also check roll_number
                if not db.query(Student).filter(Student.roll_number == s["roll"]).first():
                    student = Student(user_id=user_id, roll_number=s["roll"], branch=s["branch"], batch_year=2021, current_year=s["year"], readiness_score=0.0, profile_completion_percent=10.0)
                    db.add(student); db.commit(); print(f"DB created: {s['email']}")
                else: print(f"Roll conflict: {s['roll']}")
            else: print(f"DB already exists: {s['email']}")

    # 2. Seed Faculty
    print("\n--- Seeding Faculty ---")
    for f in faculties:
        res = requests.post(f"{SUPABASE_URL}/auth/v1/admin/users", headers=headers, json={
            "email": f["email"], "password": f["password"], "email_confirm": True,
            "user_metadata": {"full_name": f["full_name"], "role": "faculty"}
        })
        user_id = None
        if res.status_code in [200, 201]: user_id = res.json()["id"]; print(f"Auth created: {f['email']}")
        else:
            res_list = requests.get(f"{SUPABASE_URL}/auth/v1/admin/users", headers=headers)
            for u in res_list.json().get('users', []):
                if u['email'] == f['email']: user_id = u['id']; break
            print(f"Auth existing/checked: {f['email']}")

        if user_id:
            existing = db.query(Faculty).filter(Faculty.user_id == user_id).first()
            if not existing:
                # Also check employee_id
                if not db.query(Faculty).filter(Faculty.employee_id == f["emp_id"]).first():
                    faculty = Faculty(user_id=user_id, employee_id=f["emp_id"], department=f["dept"], designation="Professor")
                    db.add(faculty); db.commit(); print(f"DB created: {f['email']}")
                else: print(f"EmployeeID conflict: {f['emp_id']}")
            else: print(f"DB already exists: {f['email']}")
    db.close()

if __name__ == "__main__": seed()
