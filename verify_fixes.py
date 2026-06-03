import requests
import json
import uuid
import time
from datetime import datetime, timedelta

BASE_URL = "http://127.0.0.1:8000/api/v1"
STUDENT_TOKEN = "mock_valid_00000000-0000-0000-0000-000000000001"
FACULTY_TOKEN = "mock_valid_00000000-0000-0000-0000-000000000002"

def verify_fixes():
    # 1. Create assessment for testing
    now = datetime.utcnow()
    a_payload = {
        "title": "Fix Verification " + str(int(time.time())),
        "description": "Fix verification description",
        "type": "placement_test",
        "duration": 45,
        "maxScore": 100,
        "passingScore": 40,
        "is_published": True,
        "start_time": (now - timedelta(hours=1)).isoformat() + "Z",
        "end_time": (now + timedelta(hours=5)).isoformat() + "Z",
        "departments": ["computer_science"],
        "batches": ["fourth"]
    }
    a_res = requests.post(f"{BASE_URL}/assessments/", headers={"Authorization": f"Bearer {FACULTY_TOKEN}"}, json=a_payload).json()
    aid = a_res["data"]["id"]
    print(f"Created Assessment: {aid}")

    # Add MCQ question
    q1_payload = {
        "title": "MCQ Verification",
        "difficulty": "easy",
        "question_type": "mcq",
        "description": "What is 2+2? (Must be at least 20 chars)",
        "options": [{"id": 1, "text": "3"}, {"id": 2, "text": "4"}],
        "solution_code": {"correct_option": 2},
        "max_score": 10
    }
    q1_res = requests.post(f"{BASE_URL}/questions/", headers={"Authorization": f"Bearer {FACULTY_TOKEN}"}, json=q1_payload).json()
    qid1 = q1_res["data"]["id"]
    
    # Add Coding question
    q2_payload = {
        "title": "Coding Verification",
        "difficulty": "medium",
        "question_type": "coding",
        "description": "Write a function to add two numbers. (Must be at least 20 chars)",
        "input_format": "a, b",
        "output_format": "sum",
        "constraints": "none",
        "sample_test_cases": [{"input": "1 2", "output": "3"}],
        "starter_code": {"python": "def add(a, b): pass"},
        "max_score": 20
    }
    q2_res = requests.post(f"{BASE_URL}/questions/", headers={"Authorization": f"Bearer {FACULTY_TOKEN}"}, json=q2_payload).json()
    qid2 = q2_res["data"]["id"]

    requests.post(f"{BASE_URL}/assessments/{aid}/questions", headers={"Authorization": f"Bearer {FACULTY_TOKEN}"}, json={"question_id": qid1, "marks": 10, "question_order": 1})
    requests.post(f"{BASE_URL}/assessments/{aid}/questions", headers={"Authorization": f"Bearer {FACULTY_TOKEN}"}, json={"question_id": qid2, "marks": 20, "question_order": 2})

    # Fix 1 Verification
    print("\n--- VERIFYING FIX 1: GET /assessments/{id} ---")
    res1 = requests.get(f"{BASE_URL}/assessments/{aid}", headers={"Authorization": f"Bearer {FACULTY_TOKEN}"}).json()
    questions = res1["data"]["questions"]
    print(f"Question count: {len(questions)}")
    for q in questions:
        print(f"Question Type: {q['question_type']}")
        for field in ["description", "input_format", "output_format", "constraints", "sample_test_cases", "starter_code", "options"]:
            exists = field in q
            val_present = q[field] is not None if field != "sample_test_cases" else len(q[field]) > 0
            print(f"  {field}: {'✅' if exists else '❌'} (Present: {val_present})")

    # Fix 3 Verification (part of start attempt)
    print("\n--- VERIFYING FIX 3: POST /assessments/{id}/attempt/start ---")
    res_start_full = requests.post(f"{BASE_URL}/assessments/{aid}/attempt/start", headers={"Authorization": f"Bearer {STUDENT_TOKEN}"})
    res_start = res_start_full.json()
    if res_start_full.status_code != 200:
        print(f"❌ POST start failed ({res_start_full.status_code}): {res_start}")
        return
    print(f"Success: {res_start.get('success')}")
    print(f"time_limit_minutes: {res_start.get('data', {}).get('time_limit_minutes')} {'✅' if 'time_limit_minutes' in res_start.get('data', {}) else '❌'}")
    att_id = res_start.get('data', {}).get('attempt_id')

    # Fix 2 Verification
    print("\n--- VERIFYING FIX 2: GET /assessments/my ---")
    # First submit the attempt
    submit_payload = {
        "attempt_id": att_id,
        "time_taken_minutes": 5,
        "tab_switch_count": 0,
        "answers": [{"question_id": qid1, "question_type": "mcq", "selected_option": 2}],
        "proctoring_events": []
    }
    requests.post(f"{BASE_URL}/assessments/{aid}/attempt/submit", headers={"Authorization": f"Bearer {STUDENT_TOKEN}"}, json=submit_payload)
    
    res_my = requests.get(f"{BASE_URL}/assessments/my", headers={"Authorization": f"Bearer {STUDENT_TOKEN}"}).json()
    found = False
    for a in res_my["data"]:
        if a["id"] == aid:
            found = True
            print(f"Assessment found in 'my' list.")
            print(f"  attempted: {a.get('attempted')} {'✅' if 'attempted' in a else '❌'}")
            print(f"  attempt_id: {a.get('attempt_id')} {'✅' if 'attempt_id' in a else '❌'}")
            print(f"  score: {a.get('score')} {'✅' if 'score' in a else '❌'}")
    if not found:
        print("❌ Test assessment not found in 'my' list.")

if __name__ == "__main__":
    verify_fixes()
