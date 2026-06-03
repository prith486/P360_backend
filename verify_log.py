import requests, json

BASE = "http://localhost:8000/api/v1"

def log(msg):
    with open("verify_final_report.txt", "a", encoding="utf-8") as f:
        f.write(str(msg) + "\n")

# Clear file
open("verify_final_report.txt", "w").close()

ft = requests.post(f"{BASE}/auth/mock-login", json={"role": "faculty"}).json()["access_token"]
fh = {"Authorization": f"Bearer {ft}"}

r = requests.get(f"{BASE}/faculty/dashboard", headers=fh)
log(f"Status: {r.status_code}")

if r.status_code == 200:
    data = r.json().get("data", {})
    
    # Check existing fields
    log("\n=== EXISTING FIELDS ===")
    log(f"profile: {bool(data.get('profile'))}")
    log(f"stats: {data.get('stats')}")
    
    # Check new readiness analytics
    log("\n=== READINESS ANALYTICS ===")
    ra = data.get("readiness_analytics", {})
    if ra:
        log(f"average_score: {ra.get('average_score')}")
        log(f"total_students: {ra.get('total_students')}")
        log(f"placement_ready_count: {ra.get('placement_ready_count')}")
        log(f"at_risk_count: {ra.get('at_risk_count')}")
        log(f"segmentation: {ra.get('segmentation')}")
        log(f"score_distribution: {ra.get('score_distribution')}")
        log(f"branch_performance: {ra.get('branch_performance')}")
    else:
        log("readiness_analytics: MISSING")
    
    # Check at-risk students
    log("\n=== AT-RISK STUDENTS ===")
    at_risk = data.get("at_risk_students", [])
    log(f"count: {len(at_risk)}")
    for s in at_risk:
        log(f"  {s.get('name')} -- score: {s.get('readiness_score')}")
    
    # Check top performers
    log("\n=== TOP PERFORMERS ===")
    top = data.get("top_performers", [])
    log(f"count: {len(top)}")
    for s in top:
        log(f"  {s.get('name')} -- score: {s.get('readiness_score')}")
else:
    log(f"Error: {r.text[:300]}")

# Also check student results endpoints
log("\n=== STUDENT RESULTS ENDPOINTS ===")
st = requests.post(f"{BASE}/auth/mock-login", json={"role": "student"}).json()["access_token"]
sh = {"Authorization": f"Bearer {st}"}

# Check what attempt history endpoints exist
attempt_endpoints = [
    f"/students/me/attempts",
    f"/students/me/results", 
    f"/assessments/my-attempts",
]
for p in attempt_endpoints:
    r2 = requests.get(f"{BASE}{p}", headers=sh)
    log(f"GET {p}: {r2.status_code}")

# Check if assessment attempts exist for the seeded student
r3 = requests.get(f"{BASE}/assessments/my", headers=sh)
log(f"\nGET /assessments/my: {r3.status_code}")
if r3.status_code == 200:
    assessments = r3.json().get("data", [])
    attempted = [a for a in assessments if a.get("attempted")]
    log(f"Total assessments: {len(assessments)}")
    log(f"Attempted: {len(attempted)}")
    for a in attempted:
        log(f"  {a.get('title')} -- score: {a.get('score')}, attempt_id: {a.get('attempt_id')}")
