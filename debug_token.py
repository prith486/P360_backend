import requests, json
from jose import jwt

BASE = "http://localhost:8000/api/v1"

def debug_student_token():
    print("\n--- DEBUG: STUDENT TOKEN ---")
    r = requests.post(f"{BASE}/auth/mock-login", json={"role": "student"})
    print(f"Login Status: {r.status_code}")
    data = r.json()
    token = data.get("access_token")
    print(f"Token: {token[:20]}...")
    
    # Local decode without verification (just to see)
    payload = jwt.get_unverified_claims(token)
    print(f"Payload: {payload}")
    print(f"Role type: {type(payload.get('role'))}")
    print(f"Role value: '{payload.get('role')}'")
    print(f"Comparison 'student' == role: {'student' == payload.get('role')}")

if __name__ == "__main__":
    debug_student_token()
