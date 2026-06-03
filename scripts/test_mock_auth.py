"""
End-to-end smoke test for the new mock auth endpoints.
Run: .\venv\Scripts\python.exe scripts\test_mock_auth.py
"""
import urllib.request, json

BASE = "http://localhost:8000/api/v1/auth"


def request(method, path, body=None, token=None):
    url = BASE + path
    headers = {"Content-Type": "application/json"}
    if token:
        headers["Authorization"] = f"Bearer {token}"
    data = json.dumps(body).encode() if body else None
    req = urllib.request.Request(url, data=data, headers=headers, method=method)
    try:
        with urllib.request.urlopen(req, timeout=10) as resp:
            return resp.status, json.loads(resp.read())
    except urllib.error.HTTPError as e:
        return e.code, json.loads(e.read())


print("=" * 60)
print("TEST 1 — mock-login as student")
status, resp = request("POST", "/mock-login", {"role": "student"})
print(f"  {status} → {'✅ PASS' if status == 200 else '❌ FAIL'}")
student_token = resp.get("access_token", "")
print(f"  Token: {student_token[:60]}...")
print(f"  User:  {resp.get('user')}")

print()
print("=" * 60)
print("TEST 2 — mock-login as faculty")
status, resp = request("POST", "/mock-login", {"role": "faculty"})
print(f"  {status} → {'✅ PASS' if status == 200 else '❌ FAIL'}")
faculty_token = resp.get("access_token", "")
print(f"  Token: {faculty_token[:60]}...")
print(f"  User:  {resp.get('user')}")

print()
print("=" * 60)
print("TEST 3 — mock-me with student token")
status, resp = request("GET", "/mock-me", token=student_token)
print(f"  {status} → {'✅ PASS' if status == 200 else '❌ FAIL'}")
print(f"  Data:  {resp.get('data')}")

print()
print("=" * 60)
print("TEST 4 — GET /auth/me with mock-login token (real endpoint)")
url = "http://localhost:8000/api/v1/auth/me"
req = urllib.request.Request(url, headers={"Authorization": f"Bearer {student_token}"}, method="GET")
try:
    with urllib.request.urlopen(req, timeout=10) as resp:
        data = json.loads(resp.read())
        print(f"  {resp.status} → {'✅ PASS' if resp.status == 200 else '❌ FAIL'}")
        print(f"  Data:  {data}")
except urllib.error.HTTPError as e:
    print(f"  {e.code} → ❌ FAIL: {e.read().decode()}")

print()
print("=" * 60)
print("TEST 5 — GET /students/dashboard with mock-login token (real endpoint)")
url = "http://localhost:8000/api/v1/students/dashboard"
req = urllib.request.Request(url, headers={"Authorization": f"Bearer {student_token}"}, method="GET")
try:
    with urllib.request.urlopen(req, timeout=10) as resp:
        data = json.loads(resp.read())
        print(f"  {resp.status} → {'✅ PASS' if resp.status == 200 else '❌ FAIL'}")
        print(f"  Has profile key: {'profile' in data.get('data', {})}")
except urllib.error.HTTPError as e:
    print(f"  {e.code} → ❌ FAIL: {e.read().decode()[:200]}")

print()
print("=" * 60)
print("TEST 6 — mock-login DISABLED check (invalid role should return 422)")
status, resp = request("POST", "/mock-login", {"role": "admin"})
print(f"  {status} → {'✅ PASS (validation error)' if status == 422 else '❌ FAIL'}")
