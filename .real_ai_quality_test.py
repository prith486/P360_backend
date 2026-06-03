import json
import requests

BASE = "http://127.0.0.1:8002/api/v1"
TOKEN = "mock_valid_faculty_00000000-0000-0000-0000-000000000002"
HEADERS = {"Authorization": f"Bearer {TOKEN}", "Content-Type": "application/json"}


def validate_question(item):
    issues = []
    qtype = str(item.get("type", "")).lower().strip()
    text = str(item.get("question_text", "")).strip()
    if len(text) < 20:
        issues.append("question_text too short")
    if qtype not in {"mcq", "coding"}:
        issues.append("invalid type")

    if qtype == "mcq":
        options = item.get("options") if isinstance(item.get("options"), dict) else {}
        for k in ["A", "B", "C", "D"]:
            if not str(options.get(k, "")).strip():
                issues.append(f"missing option {k}")
        if str(item.get("correct_option", "")).upper() not in {"A", "B", "C", "D"}:
            issues.append("invalid correct_option")

    if qtype == "coding":
        starter = item.get("starter_code") if isinstance(item.get("starter_code"), dict) else {}
        if not isinstance(starter, dict):
            issues.append("starter_code missing")
        sample = item.get("sample_test_cases") if isinstance(item.get("sample_test_cases"), list) else []
        if len(sample) == 0:
            issues.append("sample_test_cases empty")

    if not str(item.get("explanation", "")).strip():
        issues.append("explanation missing")

    return issues

print("=== Real AI Provider Quality Test (port 8002) ===")

# 1) Questions generate (real AI call)
q_payload = {
    "topic": "Dynamic Programming",
    "difficulty": "medium",
    "question_type": "mixed",
    "count": 2,
    "role_tags": ["SDE"],
    "company_tags": ["Amazon"],
    "additional_instructions": "Campus placement level, avoid trivial questions.",
}
q_res = requests.post(f"{BASE}/questions/generate", headers=HEADERS, data=json.dumps(q_payload), timeout=240)
print("questions/generate status:", q_res.status_code)
print("questions/generate body preview:", q_res.text[:350].replace("\n", " "))

if q_res.status_code != 200:
    raise SystemExit(1)

q_json = q_res.json()
questions = q_json.get("questions", [])
print("generated count:", len(questions))

all_issues = []
for idx, item in enumerate(questions):
    issues = validate_question(item)
    if issues:
        all_issues.append({"index": idx, "issues": issues})

print("quality issues:", all_issues if all_issues else "none")
if questions:
    print("sample question type:", questions[0].get("type"))
    print("sample question text:", str(questions[0].get("question_text", ""))[:180])

# 2) Save one generated question
save_payload = {"questions": questions[:1]}
s_res = requests.post(f"{BASE}/questions/generate/save", headers=HEADERS, data=json.dumps(save_payload), timeout=120)
print("questions/generate/save status:", s_res.status_code)
print("questions/generate/save body:", s_res.text[:300])

# 3) Assessment generate (real AI may be used for deficits)
a_payload = {
    "title": "AI Provider Quality Assessment Probe",
    "topic_distribution": [
        {"topic": "Bit Manipulation", "easy": 0, "medium": 1, "hard": 1, "expert": 0}
    ],
    "question_type_mix": "mixed",
    "target_cgpa_min": 7.0,
    "duration_minutes": 45,
    "existing_question_ids": []
}
a_res = requests.post(f"{BASE}/assessments/generate", headers=HEADERS, data=json.dumps(a_payload), timeout=240)
print("assessments/generate status:", a_res.status_code)
print("assessments/generate body preview:", a_res.text[:350].replace("\n", " "))

if a_res.status_code == 200:
    data = a_res.json().get("data", {})
    print("proposal totals:", {
        "total_questions": data.get("total_questions"),
        "from_bank": len(data.get("fulfilled_from_bank", [])),
        "newly_generated": len(data.get("newly_generated", [])),
        "unfilled_slots": len(data.get("unfilled_slots", [])),
    })

print("=== Done ===")
