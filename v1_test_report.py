import urllib.request
import json
import uuid

BASE_URL = "http://127.0.0.1:8000/api/v1"
FACULTY_TOKEN = "mock_valid_00000000-0000-0000-0000-000000000002"
STUDENT_TOKEN = "mock_valid_00000000-0000-0000-0000-000000000001"

def api_call(method, path, token, body=None):
    url = f"{BASE_URL}{path}"
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    }
    req = urllib.request.Request(url, headers=headers, method=method)
    if body:
        data = json.dumps(body).encode('utf-8')
        req.data = data
    
    try:
        with urllib.request.urlopen(req) as res:
            return res.status, json.load(res)
    except urllib.error.HTTPError as e:
        try:
            err_body = json.load(e)
        except:
            err_body = e.read().decode('utf-8')
        return e.code, err_body
    except Exception as e:
        return 500, str(e)

def run_report_tests():
    report = {}

    # 2. POST /api/v1/assessments/
    payload_2 = {
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
    s2, r2 = api_call("POST", "/assessments/", FACULTY_TOKEN, payload_2)
    report["step_2"] = {"status": s2, "response": r2}

    # 3. GET /api/v1/assessments/
    s3, r3 = api_call("GET", "/assessments/", FACULTY_TOKEN)
    report["step_3"] = {"status": s3, "response": r3}

    # 4. POST /api/v1/questions/
    payload_4 = {
      "title": "Two Sum",
      "difficulty": "easy",
      "question_type": "coding",
      "description": "Given an array of integers nums and an integer target, return indices of the two numbers such that they add up to target. (Min 20 chars for validation)",
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
    s4, r4 = api_call("POST", "/questions/", FACULTY_TOKEN, payload_4)
    report["step_4"] = {"status": s4, "response": r4}

    # 5. POST /api/v1/assessments/{id}/questions
    new_assessment_id = None
    if s2 == 200 or s2 == 201:
        new_assessment_id = r2.get("data", {}).get("id")
    
    new_question_id = None
    if s4 == 200 or s4 == 201:
        new_question_id = r4.get("data", {}).get("id")

    if new_assessment_id and new_question_id:
        payload_5 = {
            "question_id": new_question_id,
            "marks": 10,
            "question_order": 1
        }
        s5, r5 = api_call("POST", f"/assessments/{new_assessment_id}/questions", FACULTY_TOKEN, payload_5)
        report["step_5"] = {"status": s5, "response": r5, "request": payload_5}
    else:
        report["step_5"] = "Skipped - Assessment or Question creation failed"

    # 6. GET /api/v1/assessments/my
    s6, r6 = api_call("GET", "/assessments/my", STUDENT_TOKEN)
    report["step_6"] = {"status": s6, "response": r6}

    # 8. GET /api/v1/questions/ (Bonus for table in Q1)
    s8, r8 = api_call("GET", "/questions/", FACULTY_TOKEN)
    report["step_8"] = {"status": s8, "response": r8}

    print(json.dumps(report, indent=2))

if __name__ == "__main__":
    run_report_tests()
