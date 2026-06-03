
import sys
import os
from pathlib import Path

# Add project root to sys.path
base = Path("c:/Users/PRIHTVIRAJ/Desktop/P360_BACKEND/placement360-backend")
sys.path.append(str(base))

from app.core.database import SessionLocal
from app.models.student import Student
from app.models.auth_user import AuthUser

def audit():
    db = SessionLocal()
    try:
        students = db.query(Student).all()
        print(f"Total students in DB: {len(students)}")
        print("\n--- Student Details ---")
        for s in students:
            user = s.user
            name = user.full_name if user else "Unknown"
            email = user.email if user else "Unknown"
            print(f"Name: {name} | Roll: {s.roll_number} | Branch: {s.branch.value if hasattr(s.branch, 'value') else s.branch} | Email: {email}")
    finally:
        db.close()

if __name__ == "__main__":
    audit()
