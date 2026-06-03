import requests, json

BASE = "http://localhost:8000/api/v1"
ft = requests.post(f"{BASE}/auth/mock-login", json={"role": "faculty"}).json()["access_token"]
fh = {"Authorization": f"Bearer {ft}"}

r = requests.get(f"{BASE}/faculty/dashboard", headers=fh)
print(f"Status: {r.status_code}")

if r.status_code == 200:
    data = r.json().get("data", {})
    
    # Check existing fields
    print(f"\n=== EXISTING FIELDS ===")
    print(f"profile: {bool(data.get('profile'))}")
    print(f"stats: {data.get('stats')}")
    
    # Check new readiness analytics
    print(f"\n=== READINESS ANALYTICS ===")
    ra = data.get("readiness_analytics", {})
    if ra:
        print(f"average_score: {ra.get('average_score')}")
        print(f"total_students: {ra.get('total_students')}")
        print(f"placement_ready_count: {ra.get('placement_ready_count')}")
        print(f"at_risk_count: {ra.get('at_risk_count')}")
        print(f"segmentation: {ra.get('segmentation')}")
        print(f"score_distribution: {ra.get('score_distribution')}")
        print(f"branch_performance: {ra.get('branch_performance')}")
    else:
        print("readiness_analytics: MISSING")
    
    # Check at-risk students
    print(f"\n=== AT-RISK STUDENTS ===")
    at_risk = data.get("at_risk_students", [])
    print(f"count: {len(at_risk)}")
    for s in at_risk:
        print(f"  {s.get('name')} -- score: {s.get('readiness_score')}")
    
    # Check top performers
    print(f"\n=== TOP PERFORMERS ===")
    top = data.get("top_performers", [])
    print(f"count: {len(top)}")
    for s in top:
        print(f"  {s.get('name')} -- score: {s.get('readiness_score')}")
else:
    print(f"Error: {r.text[:300]}")

# Also check student results endpoints
print(f"\n=== STUDENT RESULTS ENDPOINTS ===")
st = requests.post(f"{BASE}/auth/mock-login", json={"role": "student"}).json()["access_token"]
sh = {"Authorization": f"Bearer {st}"}

# Check what attempt history endpoints exist
attempt_endpoints = [
    f"{BASE}/students/me/attempts",
    f"{BASE}/students/me/results", 
    f"{BASE}/assessments/my-attempts",
]
for url in attempt_endpoints:
    r2 = requests.get(url, headers=sh)
    print(f"GET {url.replace(BASE, '')}: {r2.status_code}")

# Check if assessment attempts exist for the seeded student
r3 = requests.get(f"{BASE}/assessments/my", headers=sh)
print(f"\nGET /assessments/my: {r3.status_code}")
if r3.status_code == 200:
    assessments = r3.json().get("data", [])
    attempted = [a for a in assessments if a.get("attempted")]
    print(f"Total assessments: {len(assessments)}")
    print(f"Attempted: {len(attempted)}")
    for a in attempted:
        print(f"  {a.get('title')} -- score: {a.get('score')}, attempt_id: {a.get('attempt_id')}")
