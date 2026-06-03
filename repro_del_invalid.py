import requests
API = "http://localhost:8000/api/v1"
ST = "mock_valid_student_token_00000000-0000-0000-0000-000000000001"
# Invalid platform "invalid_platform"
r = requests.delete(f"{API}/students/me/external-platform", json={"platform": "invalid_platform"}, headers={"Authorization": f"Bearer {ST}"})
print(f"Status: {r.status_code}")
print(r.text)
