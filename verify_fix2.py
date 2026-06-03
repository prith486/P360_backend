import requests
API = "http://localhost:8000/api/v1"
# Invalid email and short password
r = requests.post(f"{API}/auth/login", json={"email": "invalid", "password": "sh"})
print(f"Status: {r.status_code}")
print(r.text)
