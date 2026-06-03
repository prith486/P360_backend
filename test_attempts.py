import requests
import json
import uuid
import time
from datetime import datetime, timedelta

BASE_URL = "http://127.0.0.1:8000/api/v1"

# Mock tokens
FACULTY_TOKEN = "mock_valid_00000000-0000-0000-0000-000000000002"
STUDENT_TOKEN = "mock_valid_00000000-0000-0000-0000-000000000001"

def api_call(method, endpoint, token=None, json_data=None):
    headers = {}
    if token:
        headers["Authorization"] = f"Bearer {token}"
    
    url = f"{BASE_URL}{endpoint}"
    print(f"\n>>> {method} {endpoint}")
    if json_data:
        print(f"Payload: {json.dumps(json_data, indent=2)}")
        
    try:
        response = requests.request(method, url, headers=headers, json=json_data, timeout=30)
        print(f"Status: {response.status_code}")
        try:
            res_json = response.json()
            print(f"Response: {json.dumps(res_json, indent=2)}")
            return res_json
        except:
            print(f"Response (text): {response.text}")
            return None
    except Exception as e:
        print(f"Error: {str(e)}")
        return None

def test_flow():
    # 1. Faculty creates Assessment
    now = datetime.utcnow()
    start_time = now - timedelta(hours=1)
    end_time = now + timedelta(hours=5)
    
    assessment_payload = {
        "title": "Exam Attempt Test " + str(int(time.time())),
        "description": "Testing start and submit endpoints",
        "type": "placement_test",
        "duration": 60,
        "maxScore": 50,
        "passingScore": 20,
        "is_published": True,
        "start_time": start_time.isoformat() + "Z",
        "end_time": end_time.isoformat() + "Z"
    }
    
    a_res = api_call("POST", "/assessments/", FACULTY_TOKEN, assessment_payload)
    if not a_res or not a_res.get("success"):
        print("Failed to create assessment")
        return
    
    assessment_id = a_res["data"]["id"]
    
    # 2. Add a question
    q_payload = {
        "title": "MCQ Question " + str(int(time.time())),
        "difficulty": "easy",
        "question_type": "mcq",
        "description": "What is 2+2? (Description min 20 chars so it passes validation)",
        "options": [
            {"id": 1, "text": "3"},
            {"id": 2, "text": "4"},
            {"id": 3, "text": "5"}
        ],
        "solution_code": {"correct_option": 2},
        "max_score": 10,
        "is_public": True
    }
    q_res = api_call("POST", "/questions/", FACULTY_TOKEN, q_payload)
    if not q_res or not q_res.get("success"):
        print("Failed to create question")
        return
    
    question_id = q_res["data"]["id"]
    
    # Link question to assessment
    link_res = api_call("POST", f"/assessments/{assessment_id}/questions", FACULTY_TOKEN, {
        "question_id": question_id,
        "marks": 10,
        "question_order": 1
    })
    
    # 3. Student starts attempt
    start_res = api_call("POST", f"/assessments/{assessment_id}/attempt/start", STUDENT_TOKEN)
    if not start_res or not start_res.get("success"):
        print("Failed to start attempt")
        return
    
    attempt_id = start_res["data"]["attempt_id"]
    
    # 4. Student submits attempt
    submit_payload = {
        "attempt_id": attempt_id,
        "time_taken_minutes": 10,
        "tab_switch_count": 0,
        "answers": [
            {
                "question_id": question_id,
                "question_type": "mcq",
                "selected_option": 2
            }
        ],
        "proctoring_events": [
            {"event": "tab_switch", "timestamp": now.isoformat() + "Z"}
        ]
    }
    submit_res = api_call("POST", f"/assessments/{assessment_id}/attempt/submit", STUDENT_TOKEN, submit_payload)
    
    # 5. Faculty checks attempts
    api_call("GET", f"/assessments/{assessment_id}/attempts", FACULTY_TOKEN)
    
    # 6. Faculty checks attempt detail
    api_call("GET", f"/assessments/{assessment_id}/attempts/{attempt_id}", FACULTY_TOKEN)

if __name__ == "__main__":
    test_flow()
