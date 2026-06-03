import requests
import json
import sys

BASE = "http://127.0.0.1:8000/api/v1"

print(f"Testing connectivity to {BASE}...")

try:
    # Faculty token
    r = requests.post(f"{BASE}/auth/mock-login", json={"role": "faculty"}, timeout=10)
    res_data = r.json()
    faculty_token = res_data.get("access_token") or res_data.get("accessToken")
    fh = {"Authorization": f"Bearer {faculty_token}"}

    # Student token  
    r = requests.post(f"{BASE}/auth/mock-login", json={"role": "student"}, timeout=10)
    res_data = r.json()
    student_token = res_data.get("access_token") or res_data.get("accessToken")
    sh = {"Authorization": f"Bearer {student_token}"}

    tests = [
        ("Faculty Dashboard", "GET", f"{BASE}/faculty/dashboard", fh),
        ("Student Dashboard", "GET", f"{BASE}/students/dashboard", sh),
        ("Assessments List", "GET", f"{BASE}/assessments", fh),
        ("Assessments My", "GET", f"{BASE}/assessments/my", sh),
    ]

    print("\n--- LIVE ENDPOINT TESTS ---")
    for name, method, url, headers in tests:
        try:
            r = requests.request(method, url, headers=headers, timeout=15)
            print(f"{name}: {r.status_code}")
            if r.status_code != 200:
                print(f"  Response: {r.text[:200]}")
        except Exception as e:
            print(f"{name}: FAILED - {e}")
    print("---------------------------\n")

except Exception as e:
    print(f"CRITICAL ERROR: {e}")
