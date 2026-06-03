import requests, json
API = "http://localhost:8000/api/v1"
ST = "mock_valid_student_token_00000000-0000-0000-0000-000000000001"

def t(label, method, url, body=None):
    r = getattr(requests, method)(url, json=body, headers={"Authorization": f"Bearer {ST}", "Content-Type": "application/json"})
    print(f"{label}: {r.status_code}")
    print(r.text[:500])

t("POST LeetCode", "post", f"{API}/students/me/external-platform", body={"platform":"leetcode","username":"testuser123"})
