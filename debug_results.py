import requests, json

BASE = "http://localhost:8000/api/v1"

def debug_all():
    # Login as Student
    print("\n=== STUDENT ME RESULTS ===")
    st = requests.post(f"{BASE}/auth/mock-login", json={"role": "student"}).json()["access_token"]
    sh = {"Authorization": f"Bearer {st}"}
    r = requests.get(f"{BASE}/students/me/results", headers=sh)
    print(f"Status: {r.status_code}")
    print(json.dumps(r.json(), indent=2))
    
    # Login as Faculty
    print("\n=== FACULTY DASHBOARD ===")
    ft = requests.post(f"{BASE}/auth/mock-login", json={"role": "faculty"}).json()["access_token"]
    fh = {"Authorization": f"Bearer {ft}"}
    r = requests.get(f"{BASE}/faculty/dashboard", headers=fh)
    print(f"Status: {r.status_code}")
    if r.status_code == 200:
        data = r.json().get("data", {})
        print(f"Readiness Analytics: {json.dumps(data.get('readiness_analytics'), indent=2)}")
        print(f"\nAt-Risk Students (names): {[s['name'] for s in data.get('at_risk_students', [])]}")
        print(f"Top Performers (names): {[s['name'] for s in data.get('top_performers', [])]}")

if __name__ == "__main__":
    debug_all()
