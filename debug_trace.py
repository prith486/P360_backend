import requests, json, traceback

BASE = "http://localhost:8000/api/v1"

def debug_full():
    try:
        st = requests.post(f"{BASE}/auth/mock-login", json={"role": "student"}).json()["access_token"]
        sh = {"Authorization": f"Bearer {st}"}
        r = requests.get(f"{BASE}/students/me/results", headers=sh)
        print(f"Status: {r.status_code}")
        print(f"Response: {r.text}")
    except:
        traceback.print_exc()

if __name__ == "__main__":
    debug_full()
