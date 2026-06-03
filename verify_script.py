import requests, time

BASE = "http://localhost:8000/api/v1"

# Seed data first
import subprocess
print("Running seed...")
subprocess.run(["venv\\Scripts\\python", "seed_readiness_data.py"])
time.sleep(1)

ft = requests.post(f"{BASE}/auth/mock-login", json={"role": "faculty"}).json()["access_token"]
st = requests.post(f"{BASE}/auth/mock-login", json={"role": "student"}).json()["access_token"]
fh = {"Authorization": f"Bearer {ft}"}
sh = {"Authorization": f"Bearer {st}"}

# Recalculate all
r1 = requests.post(f"{BASE}/students/analytics/recalculate-all", headers=fh)
print(f"Recalculate all: {r1.status_code}")
data = r1.json().get("data", {})
print(f"  Updated: {data.get('updated')}, Errors: {data.get('errors')}")
for s in data.get("scores", []):
    print(f"  {s['roll_number']}: {s['score']} ({s['status']})")

# Student score breakdown
r2 = requests.get(f"{BASE}/students/me/score-breakdown", headers=sh)
print(f"\nScore breakdown: {r2.status_code}")
bd = r2.json().get("data", {})
print(f"  Total: {bd.get('total')}")
print(f"  Status: {bd.get('status')}")
comps = bd.get("components", {})
for name, c in comps.items():
    print(f"  {name}: {c.get('score')} (weighted: {c.get('weighted')})")

# Batch analytics
r3 = requests.get(f"{BASE}/students/analytics/batch", headers=fh)
print(f"\nBatch analytics: {r3.status_code}")
ba = r3.json().get("data", {})
print(f"  Total students: {ba.get('total_students')}")
print(f"  Average score: {ba.get('average_score')}")
print(f"  Segmentation: {ba.get('segmentation')}")
print(f"  Branch averages: {ba.get('branch_averages')}")
print(f"  At-risk count: {ba.get('at_risk_count')}")
