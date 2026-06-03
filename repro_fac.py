import requests
API = "http://localhost:8000/api/v1"
FT = "mock_valid_faculty_token_00000000-0000-0000-0000-000000000002"
r = requests.get(f"{API}/faculty/me", headers={"Authorization": f"Bearer {FT}"})
print(f"Status: {r.status_code}")
print(r.text)
