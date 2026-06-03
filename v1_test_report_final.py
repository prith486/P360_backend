import requests
import json
import uuid

BASE_URL = "http://127.0.0.1:8000/api/v1"
FACULTY_TOKEN = "mock_valid_00000000-0000-0000-0000-000000000002"
STUDENT_TOKEN = "mock_valid_00000000-0000-0000-0000-000000000001"

def api_call(method, path, token, json_data=None):
    url = f"{BASE_URL}{path}"
    headers = {"Authorization": f"Bearer {token}"}
    try:
        if method == "POST":
            res = requests.post(url, headers=headers, json=json_data, timeout=30)
        elif method == "GET":
            res = requests.get(url, headers=headers, timeout=30)
        elif method == "PATCH":
            res = requests.patch(url, headers=headers, json=json_data, timeout=30)
        
        try:
            return res.status_code, res.json()
        except:
            return res.status_code, res.text
    except Exception as e:
        return 500, str(e)

def run_report_tests():
    report = {}
    
    # 2. POST /api/v1/assessments/
    p2 = {
      "title": "DSA Fundamentals Test",
      "description": "Covers arrays, linked lists, trees",
      "assessment_type": "placement_test",
      "duration_minutes": 60,
      "total_marks": 100,
      "passing_marks": 40,
      "target_branches": ["computer_science"],
      "target_years": ["fourth"],
      "is_published": False,
      "enable_proctoring": True,
      "track_tab_switches": True,
      "instructions": "Do not switch tabs.",
      "max_attempts": 1
    }
    s2, r2 = api_call("POST", "/assessments/", FACULTY_TOKEN, p2)
    report["step_2"] = {"status": s2, "response": r2}

    # 3. GET /api/v1/assessments/
    s3, r3 = api_call("GET", "/assessments/", FACULTY_TOKEN)
    report["step_3"] = {"status": s3, "response": r3}

    # 4. POST /api/v1/questions/
    p4 = {
      "title": "Two Sum",
      "difficulty": "easy",
      "question_type": "coding",
      "description": "Given an array of integers nums and an integer target, return indices of the two numbers such that they add up to target. (Description min 20 chars)",
      "input_format": "First line: n (array size), Second line: n integers, Third line: target",
      "output_format": "Two indices separated by space",
      "constraints": "2 <= n <= 10^4, -10^9 <= nums[i] <= 10^9",
      "sample_test_cases": [
        { "input": "4\n2 7 11 15\n9", "output": "0 1", "explanation": "nums[0] + nums[1] = 9" }
      ],
      "hidden_test_cases": [
        { "input": "3\n3 2 4\n6", "output": "1 2" }
      ],
      "starter_code": {
        "python": "def twoSum(nums, target):\n    pass",
        "cpp": "vector<int> twoSum(vector<int>& nums, int target) {\n    \n}",
        "java": "public int[] twoSum(int[] nums, int target) {\n    \n}",
        "javascript": "var twoSum = function(nums, target) {\n    \n};"
      },
      "max_score": 10,
      "time_limit_seconds": 2,
      "memory_limit_mb": 256,
      "tags": ["arrays", "hash-map"],
      "is_public": True
    }
    s4, r4 = api_call("POST", "/questions/", FACULTY_TOKEN, p4)
    report["step_4"] = {"status": s4, "response": r4}

    # 5. POST /api/v1/assessments/{id}/questions
    aid = None
    if s2 in [200, 201]: aid = r2.get("data", {}).get("id")
    qid = None
    if s4 in [200, 201]: qid = r4.get("data", {}).get("id")

    if aid and qid:
        p5 = {"question_id": qid, "marks": 10, "question_order": 1}
        s5, r5 = api_call("POST", f"/assessments/{aid}/questions", FACULTY_TOKEN, p5)
        report["step_5"] = {"status": s5, "response": r5, "request": p5}
    else:
        report["step_5"] = f"Skipped (AID: {aid}, QID: {qid})"

    # 6. GET /api/v1/assessments/my
    s6, r6 = api_call("GET", "/assessments/my", STUDENT_TOKEN)
    report["step_6"] = {"status": s6, "response": r6}
    
    # 1. Endpoint Summary Check
    eb = {}
    eb["1. POST /assessments/"] = "YES" if s2 in [200, 201] else "NO"
    eb["2. GET /assessments/"] = "YES" if s3 == 200 else "NO"
    eb["4. GET /assessments/my"] = "YES" if s6 == 200 else "NO"
    eb["6. POST /assessments/{id}/questions"] = "YES" if report.get("step_5") != "Skipped" and report["step_5"].get("status") in [200, 201] else "NO"
    eb["7. POST /questions/"] = "YES" if s4 in [200, 201] else "NO"
    
    # Missing from report run but checked via earlier research
    # 3. GET /assessments/{id}
    if aid:
        s3_1, r3_1 = api_call("GET", f"/assessments/{aid}", FACULTY_TOKEN)
        eb["3. GET /assessments/{id}"] = "YES" if s3_1 == 200 else "NO"
        report["step_3_1"] = {"status": s3_1, "response": r3_1}
    else:
        eb["3. GET /assessments/{id}"] = "PENDING"
        
    # 5. PATCH /assessments/{id}/publish
    if aid:
        s5_1, r5_1 = api_call("PATCH", f"/assessments/{aid}/publish", FACULTY_TOKEN)
        eb["5. PATCH /assessments/{id}/publish"] = "YES" if s5_1 == 200 else "NO"
        report["step_5_1"] = {"status": s5_1, "response": r5_1}
    else:
        eb["5. PATCH /assessments/{id}/publish"] = "PENDING"

    # 8. GET /questions/
    s8, r8 = api_call("GET", "/questions/", FACULTY_TOKEN)
    eb["8. GET /questions/"] = "YES" if s8 == 200 else "NO"
    report["step_8"] = {"status": s8, "response": r8}

    report["summary_table"] = eb
    print(json.dumps(report, indent=2))

if __name__ == "__main__":
    run_report_tests()
