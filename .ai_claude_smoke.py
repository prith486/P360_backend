import json
import requests

BASE = "http://127.0.0.1:8003/api/v1"
TOKEN = "mock_valid_faculty_00000000-0000-0000-0000-000000000002"
HEADERS = {"Authorization": f"Bearer {TOKEN}", "Content-Type": "application/json"}

payload = {
    "topic": "Dynamic Programming",
    "difficulty": "medium",
    "question_type": "mixed",
    "count": 2,
    "role_tags": ["SDE"],
    "company_tags": ["Amazon"],
    "additional_instructions": "Campus placement level"
}

r = requests.post(f"{BASE}/questions/generate", headers=HEADERS, data=json.dumps(payload), timeout=240)
print("status:", r.status_code)
print("body_preview:", r.text[:500].replace("\n", " "))
if r.status_code == 200:
    data = r.json()
    qs = data.get("questions", [])
    print("count:", len(qs))
    for i, q in enumerate(qs[:2], 1):
        print(f"q{i}_type:", q.get("type"))
        print(f"q{i}_text:", str(q.get("question_text", ""))[:160])
