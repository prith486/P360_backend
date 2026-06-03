import requests
BASE = "http://localhost:8000/api/v1"
r1 = requests.post(f"{BASE}/auth/login", json={"email": "drpriya@placement360.dev", "password": "Faculty@123"})
print(f"UID from Login: {r1.json().get('user_id')}")
