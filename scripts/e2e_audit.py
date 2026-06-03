import os, requests, json

BASE = "http://localhost:8000/api/v1"

# Get tokens
faculty_token = requests.post(f"{BASE}/auth/mock-login", json={"role": "faculty"}).json()["access_token"]
student_token = requests.post(f"{BASE}/auth/mock-login", json={"role": "student"}).json()["access_token"]

fh = {"Authorization": f"Bearer {faculty_token}", "Content-Type": "application/json"}
sh = {"Authorization": f"Bearer {student_token}", "Content-Type": "application/json"}

results = []

def test(name, condition, detail=""):
    status = "✅ PASS" if condition else "❌ FAIL"
    results.append(f"{status} | {name}" + (f" | {detail}" if detail else ""))
    print(results[-1])

# ─────────────────────────────────────────
# 1. QUESTION BANK
# ─────────────────────────────────────────

# Create MCQ question
mcq = requests.post(f"{BASE}/questions/", headers=fh, json={
    "title": "What is O(1) complexity?",
    "difficulty": "easy",
    "question_type": "mcq",
    "description": "Which operation has O(1) time complexity?",
    "options": ["Array traversal", "Binary search", "Array index access", "Merge sort"],
    "correct_option": 2,
    "max_score": 2,
    "time_limit_seconds": 30,
    "memory_limit_mb": 256,
    "tags": ["arrays", "complexity"],
    "is_public": True,
    "solution_code": {"correct_option": 2}
}).json()
test("Create MCQ question", mcq.get("success"), mcq.get("data", {}).get("id", str(mcq)))
mcq_id = mcq.get("data", {}).get("id")

# Create coding question
coding = requests.post(f"{BASE}/questions/", headers=fh, json={
    "title": "Two Sum",
    "difficulty": "easy",
    "question_type": "coding",
    "description": "Find two numbers that add to target",
    "input_format": "Array and target",
    "output_format": "Two indices",
    "constraints": "2 <= n <= 10^4",
    "sample_test_cases": [{"input": "4\n2 7 11 15\n9", "output": "0 1"}],
    "hidden_test_cases": [{"input": "3\n3 2 4\n6", "output": "1 2"}],
    "starter_code": {"python": "def twoSum(nums, target):\n    pass", "cpp": "// solution", "java": "// solution", "javascript": "// solution"},
    "max_score": 10,
    "time_limit_seconds": 2,
    "memory_limit_mb": 256,
    "tags": ["arrays"],
    "is_public": True
}).json()
test("Create Coding question", coding.get("success"), coding.get("data", {}).get("id", str(coding)))
coding_id = coding.get("data", {}).get("id")

# Fetch question bank
qbank = requests.get(f"{BASE}/questions/", headers=fh).json()
test("GET question bank returns list", isinstance(qbank.get("data"), list))
test("Question bank has questions", len(qbank.get("data", [])) > 0, f"count={len(qbank.get('data', []))}")

# ─────────────────────────────────────────
# 2. ASSESSMENT CREATION
# ─────────────────────────────────────────

assessment = requests.post(f"{BASE}/assessments/", headers=fh, json={
    "title": "End to End Test Assessment",
    "description": "Full flow test",
    "type": "placement_test",
    "duration": 60,
    "maxScore": 12,
    "passingScore": 5,
    "departments": ["computer_science"],
    "batches": ["fourth"],
    "is_published": False,
    "enable_proctoring": True,
    "track_tab_switches": True,
    "instructions": "Do not switch tabs",
    "max_attempts": 1
}).json()
test("Create assessment as draft", assessment.get("success"), assessment.get("data", {}).get("id", str(assessment)))
assessment_id = assessment.get("data", {}).get("id")

# Add questions
if assessment_id and mcq_id:
    add_mcq = requests.post(f"{BASE}/assessments/{assessment_id}/questions", headers=fh, json={"question_id": mcq_id, "marks": 2, "question_order": 1}).json()
    test("Add MCQ to assessment", add_mcq.get("success"), str(add_mcq))

if assessment_id and coding_id:
    add_coding = requests.post(f"{BASE}/assessments/{assessment_id}/questions", headers=fh, json={"question_id": coding_id, "marks": 10, "question_order": 2}).json()
    test("Add Coding to assessment", add_coding.get("success"), str(add_coding))

# Get assessment detail - verify questions
detail = requests.get(f"{BASE}/assessments/{assessment_id}", headers=fh).json()
questions = detail.get("data", {}).get("questions", [])
test("Assessment detail has questions", len(questions) > 0, f"count={len(questions)}")
if questions:
    q = questions[0]
    test("Question has description", bool(q.get("description")))
    test("MCQ question has options", q.get("question_type") != "mcq" or bool(q.get("options")))
    test("Coding question has starter_code", q.get("question_type") != "coding" or bool(q.get("starter_code")))

# Publish
publish = requests.patch(f"{BASE}/assessments/{assessment_id}/publish", headers=fh).json()
test("Publish assessment", publish.get("success"), str(publish))

# ─────────────────────────────────────────
# 3. STUDENT ELIGIBILITY
# ─────────────────────────────────────────

my_assessments = requests.get(f"{BASE}/assessments/my", headers=sh).json()
found = any(a.get("id") == assessment_id for a in my_assessments.get("data", []))
test("Published assessment visible to eligible student", found, f"total_in_list={len(my_assessments.get('data', []))}")

if found:
    my_assessment = next(a for a in my_assessments.get("data", []) if a.get("id") == assessment_id)
    test("Assessment has attempted field", "attempted" in my_assessment, str(list(my_assessment.keys())))
    test("Assessment not yet attempted", my_assessment.get("attempted") == False)

# ─────────────────────────────────────────
# 4. EXAM ATTEMPT FLOW
# ─────────────────────────────────────────

start = requests.post(f"{BASE}/assessments/{assessment_id}/attempt/start", headers=sh).json()
test("Start exam attempt", start.get("success"), str(start.get("data", {}).get("attempt_id", start)))
attempt_id = start.get("data", {}).get("attempt_id")
returned_questions = start.get("data", {}).get("questions", [])
test("Start returns questions", len(returned_questions) > 0, f"count={len(returned_questions)}")
test("Start returns time_limit_minutes", bool(start.get("data", {}).get("time_limit_minutes")))

if returned_questions:
    rq = returned_questions[0]
    test("Returned question has description", bool(rq.get("description")))
    test("MCQ correct answer NOT exposed to student", "solution_code" not in rq or rq.get("solution_code") is None)

# Submit attempt
if attempt_id and returned_questions:
    answers = []
    for q in returned_questions:
        if q.get("question_type") == "mcq":
            answers.append({"question_id": q["id"], "question_type": "mcq", "selected_option": 2})
        else:
            answers.append({"question_id": q["id"], "question_type": "coding", "source_code": "def twoSum(nums, target):\n    d={}\n    for i,n in enumerate(nums):\n        if target-n in d: return [d[target-n],i]\n        d[n]=i", "language": "python"})
    
    submit = requests.post(f"{BASE}/assessments/{assessment_id}/attempt/submit", headers=sh, json={
        "attempt_id": attempt_id,
        "time_taken_minutes": 10,
        "tab_switch_count": 1,
        "answers": answers,
        "proctoring_events": [{"event": "tab_switch", "timestamp": "2026-03-22T10:00:00"}]
    }).json()
    test("Submit exam", submit.get("success"), f"score={submit.get('data', {}).get('total_score')} | raw={str(submit)[:300]}")
    test("Submit returns score", submit.get("data", {}).get("total_score") is not None)
    test("Submit returns percentage", submit.get("data", {}).get("percentage") is not None)
    test("Submit returns is_passed", submit.get("data", {}).get("is_passed") is not None)

# ─────────────────────────────────────────
# 5. RESULTS
# ─────────────────────────────────────────

my_result = requests.get(f"{BASE}/assessments/{assessment_id}/my-result", headers=sh).json()
test("Student can fetch own result", my_result.get("success"), str(my_result)[:300])
test("Own result has score", my_result.get("data", {}).get("total_score") is not None)

attempts = requests.get(f"{BASE}/assessments/{assessment_id}/attempts", headers=fh).json()
test("Faculty can see attempts list", attempts.get("success"))
test("Attempts list has entries", len(attempts.get("data", [])) > 0, f"count={len(attempts.get('data', []))}")
if attempts.get("data"):
    att = attempts["data"][0]
    test("Attempt has student_name", bool(att.get("student_name") or att.get("name")))
    test("Attempt has roll_number", bool(att.get("roll_number") or att.get("rollNumber")))
    test("Attempt has percentage", att.get("percentage") is not None)
    test("Attempt has tab_switch_count", att.get("tab_switch_count") is not None)
    test("Attempt has is_passed", att.get("is_passed") is not None)
    att_id = att.get("id") or att.get("attempt_id")
    
    if att_id:
        det = requests.get(f"{BASE}/assessments/{assessment_id}/attempts/{att_id}", headers=fh).json()
        test("Faculty can see attempt detail", det.get("success"), str(det)[:200])
        breakdown = det.get("data", {}).get("question_breakdown", [])
        test("Attempt detail has question breakdown", len(breakdown) > 0, f"count={len(breakdown)}")
        if breakdown:
            test("Breakdown has marks_awarded", breakdown[0].get("marks_awarded") is not None)
            test("Breakdown has is_correct", "is_correct" in breakdown[0])

# ─────────────────────────────────────────
# 6. AFTER ATTEMPT - STUDENT LIST UPDATE
# ─────────────────────────────────────────

my_assessments_after = requests.get(f"{BASE}/assessments/my", headers=sh).json()
after = next((a for a in my_assessments_after.get("data", []) if a.get("id") == assessment_id), None)
if after:
    test("Assessment shows attempted=True after submit", after.get("attempted") == True, f"attempted={after.get('attempted')}")
    test("Assessment shows score after submit", after.get("score") is not None, f"score={after.get('score')}")
else:
    test("Assessment shows attempted=True after submit", False, "assessment not found in list after submit")

# ─────────────────────────────────────────
# 7. SUMMARY
# ─────────────────────────────────────────

print("\n" + "="*60)
print("ASSESSMENT FEATURE - BACKEND AUDIT RESULTS")
print("="*60)
for r in results:
    print(r)

passes = sum(1 for r in results if "✅" in r)
fails = sum(1 for r in results if "❌" in r)
print(f"\nTotal: {passes} passed, {fails} failed out of {len(results)} tests")
