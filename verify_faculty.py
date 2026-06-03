import requests, json

BASE = "http://localhost:8000/api/v1"
ft = requests.post(f"{BASE}/auth/mock-login", json={"role": "faculty"}).json()["access_token"]
fh = {"Authorization": f"Bearer {ft}"}

r = requests.get(f"{BASE}/faculty/dashboard", headers=fh)
data = r.json().get("data", {})

print(f"Status: {r.status_code}")
print(f"\nreadiness_analytics:")
ra = data.get("readiness_analytics", {})
print(f"  average_score: {ra.get('average_score')}")
print(f"  segmentation: {ra.get('segmentation')}")
print(f"  branch_averages: {ra.get('branch_averages')}")
print(f"  score_distribution: {ra.get('score_distribution')}")
print(f"  branch_performance: {ra.get('branch_performance')}")

print(f"\nat_risk_students ({len(data.get('at_risk_students', []))}):")
for s in data.get("at_risk_students", []):
    print(f"  {s['name']} - score: {s['readiness_score']}")

print(f"\ntop_performers ({len(data.get('top_performers', []))}):")
for s in data.get("top_performers", []):
    print(f"  {s['name']} - score: {s['readiness_score']}")
