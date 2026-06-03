
import requests
import json

BASE = "http://localhost:8000/api/v1"

try:
    # 1. Mock login as faculty
    login_res = requests.post(f"{BASE}/auth/mock-login", json={"role": "faculty"})
    if login_res.status_code != 200:
        print(f"Login failed: {login_res.status_code}")
        exit(1)
    
    ft = login_res.json()["access_token"]
    fh = {"Authorization": f"Bearer {ft}"}

    # Task 1: Test list with all fields
    print("--- TASK 1: List Students ---")
    r = requests.get(f"{BASE}/students/", headers=fh)
    data = r.json()
    students = data.get("data", [])
    print(f"GET /students/: {r.status_code} — count: {len(students)}")
    if students:
        s = students[0]
        fields_to_check = ['readiness_score', 'skills', 'leetcode_stats', 'status']
        for f in fields_to_check:
            print(f"  Has {f}: {f in s} (Value: {s.get(f)})")

    # Task 1: Test filters
    print("\n--- TASK 1: Filters ---")
    r2 = requests.get(f"{BASE}/students/?branch=computer_science", headers=fh)
    cs_students = r2.json().get("data", [])
    print(f"Filter branch=computer_science: {r2.status_code} — count: {len(cs_students)}")

    r3 = requests.get(f"{BASE}/students/?search=aarav", headers=fh)
    search_students = r3.json().get("data", [])
    print(f"Search 'aarav': {r3.status_code} — count: {len(search_students)}")

    # Task 2: Test student detail
    print("\n--- TASK 2: Student Detail ---")
    if students:
        sid = students[0]["id"]
        r4 = requests.get(f"{BASE}/students/{sid}", headers=fh)
        detail = r4.json()
        if "data" in detail: detail = detail["data"]
        print(f"GET /students/{{id}}: {r4.status_code}")
        print(f"  Has assessment_attempts: {'assessment_attempts' in detail}")
        print(f"  Assessment count: {detail.get('assessment_count')}")
        print(f"  Average score: {detail.get('average_score')}")

    # Task 3: Test PUT update
    print("\n--- TASK 3: PUT Update ---")
    if students:
        sid = students[0]["id"]
        r5 = requests.put(f"{BASE}/students/{sid}", headers=fh, json={
            "cgpa": 9.25,
            "is_placement_ready": True,
            "skills": ["Python", "API Design", "Testing"]
        })
        print(f"PUT /students/{{id}}: {r5.status_code}")
        print(f"  Response: {r5.text[:200]}")

    # Task 4: Test POST Create
    print("\n--- TASK 4: POST Create ---")
    import random
    roll = f"TEST{random.randint(1000, 9999)}"
    r6 = requests.post(f"{BASE}/students/", headers=fh, json={
        "email": f"test_{roll}@placement360.dev",
        "full_name": "Test Student Faculty",
        "roll_number": roll,
        "branch": "computer_science",
        "batch_year": 2022,
        "current_year": "third",
        "cgpa": 8.5,
        "section": "B"
    })
    print(f"POST /students/: {r6.status_code}")
    print(f"  Response: {r6.text[:250]}")

except Exception as e:
    print(f"Error: {e}")
    import traceback
    traceback.print_exc()
