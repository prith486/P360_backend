import requests

BASE = "http://localhost:8000/api/v1"
ft = requests.post(f"{BASE}/auth/mock-login", json={"role": "faculty"}).json()["access_token"]
fh = {"Authorization": f"Bearer {ft}"}

endpoints = [
    f"{BASE}/faculty/dashboard",
    f"{BASE}/students/analytics/batch",
    f"{BASE}/students/?sort_by=readiness_score&sort_order=desc",
]

for url in endpoints:
    r = requests.get(url, headers=fh)
    print(f"\n{url}: {r.status_code}")
    if r.status_code == 200:
        import json
        print(json.dumps(r.json(), indent=2)[:400])
    else:
        print(r.text[:200])
