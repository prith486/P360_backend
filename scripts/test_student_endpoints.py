import requests
BASE = "http://localhost:8000/api/v1"
student_token = requests.post(f"{BASE}/auth/mock-login", json={"role": "student"}).json()["access_token"]
sh = {"Authorization": f"Bearer {student_token}"}

# Test existing student endpoints
endpoints = [
    ("GET /students/me", f"{BASE}/students/me"),
    ("GET /students/dashboard", f"{BASE}/students/dashboard"),
]
for name, url in endpoints:
    r = requests.get(url, headers=sh)
    print(f"{name}: {r.status_code}")
    if r.status_code == 200:
        print(f"  fields: {list(r.json().get('data', {}).keys())[:15]}")
    else:
        print(f"  error: {r.text[:100]}")
