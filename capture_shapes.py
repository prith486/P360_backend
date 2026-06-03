import requests
import json
import uuid
import time
from datetime import datetime, timedelta

BASE_URL = "http://127.0.0.1:8000/api/v1"
STUDENT_TOKEN = "mock_valid_00000000-0000-0000-0000-000000000001"
FACULTY_TOKEN = "mock_valid_00000000-0000-0000-0000-000000000002"

def get_shapes():
    # 1. GET /assessments/my
    res_my = requests.get(f"{BASE_URL}/assessments/my", headers={"Authorization": f"Bearer {STUDENT_TOKEN}"})
    print("\n--- GET /api/v1/assessments/my ---")
    data_my = res_my.json()
    if len(data_my.get("data", [])) > 1:
        data_my["data"] = data_my["data"][:1]
    print(json.dumps(data_my, indent=2))

    # Create a fresh assessment that we KNOW the student is eligible for
    now = datetime.utcnow()
    a_payload = {
        "title": "audit-test-" + str(int(time.time())),
        "description": "audit test description",
        "type": "placement_test",
        "duration": 60,
        "maxScore": 50,
        "passingScore": 20,
        "is_published": True,
        "start_time": (now - timedelta(hours=1)).isoformat() + "Z",
        "end_time": (now + timedelta(hours=5)).isoformat() + "Z",
        "departments": ["computer_science"], # Matches mock student
        "batches": ["third"] # Matches mock student
    }
    a_res = requests.post(f"{BASE_URL}/assessments/", headers={"Authorization": f"Bearer {FACULTY_TOKEN}"}, json=a_payload).json()
    aid = a_res["data"]["id"]

    # Add a question so we can see it in detail
    q_payload = {
        "title": "Audit Question",
        "difficulty": "medium",
        "question_type": "mcq",
        "description": "What is the capital of France? (Description min 20 chars)",
        "options": [{"id":1, "text": "Paris"}, {"id":2, "text": "London"}],
        "solution_code": {"correct_option": 1},
        "max_score": 10
    }
    q_res = requests.post(f"{BASE_URL}/questions/", headers={"Authorization": f"Bearer {FACULTY_TOKEN}"}, json=q_payload).json()
    qid = q_res["data"]["id"]
    
    requests.post(f"{BASE_URL}/assessments/{aid}/questions", headers={"Authorization": f"Bearer {FACULTY_TOKEN}"}, json={
        "question_id": qid, "marks": 10, "question_order": 1
    })

    # 2. GET /assessments/{id}
    res_detail = requests.get(f"{BASE_URL}/assessments/{aid}", headers={"Authorization": f"Bearer {FACULTY_TOKEN}"})
    print(f"\n--- GET /api/v1/assessments/{aid} ---")
    print(json.dumps(res_detail.json(), indent=2))

    # 3. POST /assessments/{id}/attempt/start
    res_start = requests.post(f"{BASE_URL}/assessments/{aid}/attempt/start", headers={"Authorization": f"Bearer {STUDENT_TOKEN}"})
    print(f"\n--- POST /api/v1/assessments/{aid}/attempt/start ---")
    print(json.dumps(res_start.json(), indent=2))

if __name__ == "__main__":
    get_shapes()
