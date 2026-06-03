import requests, os
from dotenv import load_dotenv
load_dotenv()

BASE = "http://localhost:8000/api/v1"
faculty_token = requests.post(f"{BASE}/auth/mock-login", json={"role": "faculty"}).json()["access_token"]
fh = {"Authorization": f"Bearer {faculty_token}", "Content-Type": "application/json"}

# Test 1 — Create MCQ question with correct format
mcq_payload = {
    "title": "What does CPU stand for?",
    "difficulty": "easy",
    "question_type": "mcq",
    "description": "Choose the correct full form of CPU (minimum length required for description field)",
    "options": [
        {"text": "Central Processing Unit", "isCorrect": True},
        {"text": "Central Program Unit", "isCorrect": False},
        {"text": "Computer Processing Unit", "isCorrect": False},
        {"text": "Core Processing Unit", "isCorrect": False}
    ],
    "max_score": 2,
    "time_limit_seconds": 30,
    "memory_limit_mb": 256,
    "tags": ["general", "hardware"],
    "is_public": True
}
mcq = requests.post(f"{BASE}/questions/", headers=fh, json=mcq_payload)
print(f"Create MCQ: {mcq.status_code}")
if mcq.status_code == 200:
    data = mcq.json().get("data", {})
    print(f"  id: {data.get('id')}")
    print(f"  options stored: {data.get('options')}")
    # Note: solution_code is only visible in QuestionDetailed, not QuestionRead (returned by POST)
    # We might need to fetch the detail to see solution_code
    q_id = data.get('id')
    detail = requests.get(f"{BASE}/questions/{q_id}", headers=fh).json()
    print(f"  detail solution_code: {detail.get('data', {}).get('solution_code')}")
else:
    print(f"  Error: {mcq.text[:600]}")

# Test 2 — Create Coding question with all fields
coding_payload = {
    "title": "Reverse a String",
    "difficulty": "easy",
    "question_type": "coding",
    "description": "Write a function that reverses a string (extended description for length check)",
    "input_format": "A single string s",
    "output_format": "The reversed string",
    "constraints": "1 <= len(s) <= 1000",
    "sample_test_cases": [
        {"input": "hello", "output": "olleh", "explanation": "Reversed hello"},
        {"input": "world", "output": "dlrow", "explanation": "Reversed world"}
    ],
    "hidden_test_cases": [
        {"input": "abcdef", "output": "fedcba"},
        {"input": "racecar", "output": "racecar"}
    ],
    "starter_code": {
        "python": "def reverseString(s):\n    # Write your solution here\n    pass",
        "cpp": "#include<string>\nusing namespace std;\nstring reverseString(string s) {\n    // Write your solution here\n}",
        "java": "public String reverseString(String s) {\n    // Write your solution here\n    return \"\";\n}",
        "javascript": "function reverseString(s) {\n    // Write your solution here\n}"
    },
    "max_score": 10,
    "time_limit_seconds": 2,
    "memory_limit_mb": 256,
    "tags": ["strings", "easy"],
    "is_public": True
}
coding = requests.post(f"{BASE}/questions/", headers=fh, json=coding_payload)
print(f"\nCreate Coding: {coding.status_code}")
if coding.status_code == 200:
    data = coding.json().get("data", {})
    print(f"  id: {data.get('id')}")
    print(f"  starter_code keys: {list(data.get('starter_code', {}).keys()) if data.get('starter_code') else 'missing'}")
    print(f"  sample_test_cases count: {len(data.get('sample_test_cases', []))}")
    # Hidden test cases won't be in QuestionRead
    q_id = data.get('id')
    detail = requests.get(f"{BASE}/questions/{q_id}", headers=fh).json()
    print(f"  detail hidden_test_cases count: {len(detail.get('data', {}).get('hidden_test_cases', [])) if detail.get('data', {}).get('hidden_test_cases') else 0}")
else:
    print(f"  Error: {coding.text[:600]}")

# Test 3 — Fetch question bank and verify fields
qbank = requests.get(f"{BASE}/questions/", headers=fh).json()
questions = qbank.get("data", [])
print(f"\nQuestion bank count: {len(questions)}")
if questions:
    q = questions[0]
    print(f"Fields in question bank response: {list(q.keys())}")
