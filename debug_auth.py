import requests
import base64
import json

BASE = "http://127.0.0.1:8000/api/v1"

try:
    # Get student token
    r = requests.post(f"{BASE}/auth/mock-login", json={"role": "student"})
    student_token = r.json()["access_token"]

    # Decode it
    parts = student_token.split(".")
    pad = parts[1] + "=" * (4 - len(parts[1]) % 4)
    payload = json.loads(base64.b64decode(pad))
    print("STUDENT TOKEN PAYLOAD:", json.dumps(payload, indent=2))

    # Test endpoints
    headers = {"Authorization": f"Bearer {student_token}"}

    r1 = requests.get(f"{BASE}/assessments/my", headers=headers)
    print(f"\nGET /assessments/my: {r1.status_code}")

    r2 = requests.get(f"{BASE}/students/dashboard", headers=headers)
    print(f"GET /students/dashboard: {r2.status_code} — {r2.text[:200]}")

    # Get faculty token
    r = requests.post(f"{BASE}/auth/mock-login", json={"role": "faculty"})
    faculty_token = r.json()["access_token"]

    parts = faculty_token.split(".")
    pad = parts[1] + "=" * (4 - len(parts[1]) % 4)
    payload = json.loads(base64.b64decode(pad))
    print("\nFACULTY TOKEN PAYLOAD:", json.dumps(payload, indent=2))

    headers2 = {"Authorization": f"Bearer {faculty_token}"}

    r3 = requests.get(f"{BASE}/faculty/dashboard", headers=headers2)
    print(f"\nGET /faculty/dashboard: {r3.status_code} — {r3.text[:200]}")

    # Test assessment detail with both tokens
    # Note: Using first assessment from /my if available, else standard ID
    ASSESSMENT_ID = "e1fb162d-6aec-4b9e-b31f-e829b41b9607"
    
    r4 = requests.get(f"{BASE}/assessments/{ASSESSMENT_ID}", headers=headers2)
    print(f"GET /assessments/{{id}} (faculty): {r4.status_code} — {r4.text[:200]}")

    r5 = requests.get(f"{BASE}/assessments/{ASSESSMENT_ID}", headers=headers)
    print(f"GET /assessments/{{id}} (student): {r5.status_code} — {r5.text[:200]}")

except Exception as e:
    print(f"ERROR: {e}")
