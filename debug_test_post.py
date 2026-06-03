import requests
import json

BASE_URL = "http://127.0.0.1:8000/api/v1"
FACULTY_TOKEN = "mock_valid_00000000-0000-0000-0000-000000000002"

def test():
    print("Testing POST /assessments/...")
    payload = {
      "title": "Debug Test " + str(id(object())),
      "description": "Debug Test Desc",
      "type": "Coding",
      "duration": 60,
      "maxScore": 100,
      "passingScore": 40
    }
    try:
        r = requests.post(f"{BASE_URL}/assessments/", headers={"Authorization": f"Bearer {FACULTY_TOKEN}"}, json=payload, timeout=5)
        print(f"Status: {r.status_code}")
        print(r.json())
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    test()
