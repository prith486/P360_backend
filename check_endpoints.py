import requests, json

BASE = "http://localhost:8000/api/v1"

def list_routes():
    # Attempting to call an endpoint with role student
    print("\n--- Testing Access to various student endpoints ---")
    st = requests.post(f"{BASE}/auth/mock-login", json={"role": "student"}).json()["access_token"]
    sh = {"Authorization": f"Bearer {st}"}
    
    endpoints = ["/students/me", "/students/me/completion", "/students/me/results"]
    for ep in endpoints:
        r = requests.get(f"{BASE}{ep}", headers=sh)
        print(f"{ep}: {r.status_code} - {r.text[:50]}")

if __name__ == "__main__":
    list_routes()
