import requests
import json

BASE = 'http://127.0.0.1:8000/api/v1'

# Faculty token
r = requests.post(f'{BASE}/auth/mock-login', json={'role': 'faculty'})
faculty_token = r.json()['access_token']
headers = {'Authorization': f'Bearer {faculty_token}'}

# Test the previously failing endpoints
endpoints = [
    ('GET', f'{BASE}/faculty/dashboard'),
    ('GET', f'{BASE}/assessments/e1fb162d-6aec-4b9e-b31f-e829b41b9607'),
]

print("--- Faculty Tests ---")
for method, url in endpoints:
    r = requests.get(url, headers=headers)
    print(f'{method} {url.split("/api/v1")[1]}: {r.status_code}')

# Student token
r = requests.post(f'{BASE}/auth/mock-login', json={'role': 'student'})
student_token = r.json()['access_token']
headers2 = {'Authorization': f'Bearer {student_token}'}

student_endpoints = [
    ('GET', f'{BASE}/students/dashboard'),
    ('GET', f'{BASE}/assessments/e1fb162d-6aec-4b9e-b31f-e829b41b9607'),
    ('GET', f'{BASE}/assessments/my'),
]

print("\n--- Student Tests ---")
for method, url in student_endpoints:
    r = requests.get(url, headers=headers2)
    print(f'{method} {url.split("/api/v1")[1]}: {r.status_code}')
