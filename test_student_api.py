import httpx
import json

def test_student_assessments():
    url = "http://localhost:8000/api/v1/assessments/my"
    headers = {"Authorization": "Bearer mock_valid_00000000-0000-0000-0000-000000000001"}
    
    try:
        res = httpx.get(url, headers=headers)
        print(f"Status: {res.status_code}")
        data = res.json()
        print(f"Success: {data.get('success')}")
        items = data.get('data', [])
        print(f"Items found: {len(items)}")
        if items:
            print("First item sample:")
            print(json.dumps(items[0], indent=2))
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    test_student_assessments()
