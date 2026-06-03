import requests
import json
import uuid

BASE_URL = "http://127.0.0.1:8000/api/v1"
STUDENT_TOKEN = "mock_valid_00000000-0000-0000-0000-000000000001"
FACULTY_TOKEN = "mock_valid_00000000-0000-0000-0000-000000000002"

def test_endpoint(name, method, path, token):
    url = f"{BASE_URL}{path}"
    headers = {"Authorization": f"Bearer {token}"}
    try:
        if method == "GET":
            res = requests.get(url, headers=headers)
        elif method == "POST":
            res = requests.post(url, headers=headers, json={})
        
        print(f"[{name}] {method} {path} -> {res.status_code}")
        if res.status_code != 200:
            print(f"  Response: {res.text}")
        return res.status_code == 200
    except Exception as e:
        print(f"[{name}] Error: {e}")
        return False

print("--- REMAINING AUDIT CHECK ---")
test_endpoint("AUTH ME", "GET", "/auth/me", STUDENT_TOKEN)
test_endpoint("STUDENTS LIST", "GET", "/students/", FACULTY_TOKEN)
test_endpoint("STUDENTS GET ID", "GET", f"/students/00000000-0000-0000-0000-000000000001", FACULTY_TOKEN) # Student 1 exists in mock
test_endpoint("STUDENTS ME", "GET", "/students/me", STUDENT_TOKEN)
test_endpoint("STUDENTS LEADERBOARD", "GET", "/students/leaderboard/", STUDENT_TOKEN)
