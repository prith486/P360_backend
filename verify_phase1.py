import requests
import json

API = "http://localhost:8000/api/v1"
ST = "mock_valid_student_token_00000000-0000-0000-0000-000000000001"
FT = "mock_valid_faculty_token_00000000-0000-0000-0000-000000000002"

# Fix #3 Tests
print("\n--- Fix #3 Test Results ---")
r1 = requests.get(f"{API}/students/me", headers={"Authorization": f"Bearer {ST}"})
print(f"- GET /students/me: {r1.status_code}")
if r1.status_code != 200: print(r1.text)

r2 = requests.get(f"{API}/faculty/me", headers={"Authorization": f"Bearer {FT}"})
print(f"- GET /faculty/me: {r2.status_code}")
if r2.status_code != 200: print(r2.text)

r3 = requests.get(f"{API}/auth/me", headers={"Authorization": f"Bearer {ST}"})
print(f"- GET /auth/me: {r3.status_code}")
if r3.status_code != 200: print(r3.text)

# Fix #4 Tests
print("\n--- Fix #4 Test Results ---")
r4 = requests.get(f"{API}/students/dashboard", headers={"Authorization": f"Bearer {ST}"})
print(f"- GET /students/dashboard: {r4.status_code}")
if r4.status_code != 200: print(r4.text)

r5 = requests.get(f"{API}/faculty/dashboard", headers={"Authorization": f"Bearer {FT}"})
print(f"- GET /faculty/dashboard: {r5.status_code}")
if r5.status_code != 200: print(r5.text)
