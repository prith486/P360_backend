import sys
import httpx
import json
from pathlib import Path
from sqlalchemy import text

# Add project root to Python path
sys.path.insert(0, str(Path(__file__).parent.parent))

from app.core.database import SessionLocal
from app.core.security import create_access_token

def get_token(email):
    """Generate JWT token for a user by email."""
    db = SessionLocal()
    try:
        user = db.execute(text("SELECT id FROM users WHERE email = :email"), {"email": email}).mappings().fetchone()
        if not user:
            print(f"User {email} not found")
            return None
        return create_access_token(subject=user.id)
    finally:
        db.close()

def test_endpoint(name, url, token, expected_status, method="GET", payload=None):
    """Test an API endpoint and verify status code."""
    headers = {"Authorization": f"Bearer {token}"} if token else {}
    if payload:
        headers["Content-Type"] = "application/json"
        response = httpx.request(method, url, headers=headers, json=payload)
    else:
        response = httpx.request(method, url, headers=headers)
        
    actual_status = response.status_code
    
    if actual_status == expected_status:
        print(f"✓ {name}: Passed (Expected {expected_status}, got {actual_status})")
    else:
        print(f"✗ {name}: Failed (Expected {expected_status}, got {actual_status})")
        print(f"  Response: {response.text}")

def run_tests():
    # Base URL
    base_url = "http://localhost:8000/api/v1"
    
    # Get tokens
    admin_token = get_token("admin@placement360.edu")
    faculty_token = get_token("faculty@placement360.edu")
    student_token = get_token("student1@placement360.edu")
    
    if not (admin_token and faculty_token and student_token):
        print("Failed to generate tokens")
        return

    print("\n--- Testing Student Endpoints ---\n")

    # 1. Student access /me
    test_endpoint("Student access /me", f"{base_url}/students/me", student_token, 200)
    
    # 2. Student list all students (Should fail)
    test_endpoint("Student list students (Forbidden)", f"{base_url}/students/", student_token, 403)
    
    # 3. Student access leaderboard
    test_endpoint("Student access leaderboard", f"{base_url}/students/leaderboard/", student_token, 200)

    print("\n--- Testing Faculty Endpoints ---\n")

    # 4. Faculty list students
    test_endpoint("Faculty list students", f"{base_url}/students/", faculty_token, 200)
    
    # 5. Faculty get specific student
    # Assuming student1 has ID 3 or similar based on previous output
    # Let's get actual ID
    db = SessionLocal()
    student_id = db.execute(text("SELECT id FROM users WHERE email = 'student1@placement360.edu'")).scalar() or 1
    db.close()
    
    # Note: API route is /students/{student_id}, where student_id is from students table, not users table.
    # We should get student.id from students table where user_id matches user.id
    db = SessionLocal()
    try:
        # Get user ID for student1 user
        user_id = db.execute(text("SELECT id FROM users WHERE email = :email"), {"email": "student1@placement360.edu"}).scalar()
        
        actual_student_id = None
        if user_id:
            actual_student_id = db.execute(text("SELECT id FROM students WHERE user_id = :user_id"), {"user_id": user_id}).scalar()
    finally:
        db.close()
    
    if actual_student_id:
        test_endpoint("Faculty get specific student", f"{base_url}/students/{actual_student_id}", faculty_token, 200)
    else:
        print("Skipping 'Faculty get specific student' test (student ID not found)")
        
    # 6. Faculty create student (Should fail)
    import uuid
    dummy_uuid = str(uuid.uuid4())
    payload = {
        "user_id": dummy_uuid, 
        "roll_number": "TEST001", 
        "branch": "computer_science", 
        "batch_year": 2024, 
        "current_year": "first"
    }
    test_endpoint("Faculty create student (Forbidden)", f"{base_url}/students/", faculty_token, 403, "POST", payload)
    
    print("\n--- Testing Unauthenticated Access ---\n")
    
    # 7. No token
    test_endpoint("No token access /me (Unauthorized)", f"{base_url}/students/me", None, 401)
    
    print("\n--- Testing Finished ---")

if __name__ == "__main__":
    run_tests()
