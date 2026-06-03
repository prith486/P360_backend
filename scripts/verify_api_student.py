import requests
import json

BASE_URL = "http://localhost:8000/api/v1"

# Need to login as Aarav (student)
login_payload = {
    "email": "test.student@placement360.dev",
    "password": "Student@123"
}

res = requests.post(f"{BASE_URL}/auth/login", json=login_payload)
if res.status_code != 200:
    print("Login failed:", res.text)
    exit(1)
else:
    token = res.json()["token"]

headers = {"Authorization": f"Bearer {token}"}

# Get assessments (student view)
res = requests.get(f"{BASE_URL}/assessments/my", headers=headers)
if res.status_code == 200:
    data = res.json()["data"]
    print(f"My assessments count: {len(data)}")
    for a in data:
         print(f"RAW ITEM: {json.dumps(a, indent=2)}")
         break
         
    # Check detail for the first one
    if data:
        aid = data[0]['id']
        res = requests.get(f"{BASE_URL}/assessments/{aid}", headers=headers)
        if res.status_code == 200:
             detail = res.json()["data"]
             print(f"\nDetail for {detail['title']}:")
             print(f"is_mine: {detail.get('is_mine')}")
             print(f"created_by_name: {detail.get('created_by_name')}")
else:
    print(f"Failed to get assessments: {res.text}")
