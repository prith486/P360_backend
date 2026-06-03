"""
Comprehensive Phase 1-5 API Test Script
Tests all endpoints defined in the frontend-backend integration plan.
"""
import json
import sys
import time
import urllib.request
import urllib.error
import urllib.parse
import uuid

BASE_URL = "http://localhost:8000/api/v1"
unique_id = uuid.uuid4().hex
TEST_EMAIL = "testuser_{:.8}@test.com".format(unique_id)
TEST_PASSWORD = "TestPass123!"
TEST_FACULTY_EMAIL = "faculty_{:.8}@test.com".format(unique_id)
STUDENT_ID = None
FACULTY_ID = None

# Token storage
auth_token = None
faculty_token = None

results = []

def req(method, path, body=None, token=None, label=None, expected_status=200):
    """Make an HTTP request and return (status_code, response_body)."""
    url = BASE_URL + path
    headers = {"Content-Type": "application/json"}
    if token:
        headers["Authorization"] = f"Bearer {token}"
    data = json.dumps(body).encode() if body else None
    request = urllib.request.Request(url, data=data, headers=headers, method=method.upper())
    try:
        with urllib.request.urlopen(request, timeout=15) as resp:
            status = resp.status
            body_text = resp.read().decode()
            try:
                resp_body = json.loads(body_text)
            except Exception:
                resp_body = body_text
            ok = status == expected_status
            tag = "✅ PASS" if ok else f"⚠️  WRONG STATUS ({status})"
            results.append((label or path, method.upper(), status, expected_status, ok, ""))
            print(f"  {tag}  [{method.upper()} {path}] → {status}")
            return status, resp_body
    except urllib.error.HTTPError as e:
        body_text = e.read().decode()
        try:
            resp_body = json.loads(body_text)
        except Exception:
            resp_body = body_text
        ok = e.code == expected_status
        tag = "✅ PASS" if ok else f"❌ FAIL ({e.code})"
        detail_raw = str(resp_body)
        error_detail = "{:.120}".format(detail_raw)
        results.append((label or path, method.upper(), e.code, expected_status, ok, error_detail))
        print(f"  {tag}  [{method.upper()} {path}] → {e.code} | {error_detail}")
        return e.code, resp_body
    except Exception as ex:
        err_msg = str(ex)
        results.append((label or path, method.upper(), "CONN_ERR", expected_status, False, f"{err_msg:.120}"))
        print(f"  ❌ CONN  [{method.upper()} {path}] → {ex}")
        return None, None


# ============================================================
# PHASE 1: Authentication
# ============================================================
print("\n" + "="*60)
print("PHASE 1 — AUTHENTICATION")
print("="*60)

print("\n[1.1] Register Student Account")
status, resp = req("POST", "/auth/register", {
    "email": TEST_EMAIL,
    "password": TEST_PASSWORD,
    "full_name": "Test Student",
    "role": "student",
    "profile_data": {
        "roll_number": f"CS{uuid.uuid4().hex[:6].upper()}",
        "branch": "computer_science",
        "batch_year": 2022,
        "current_year": "third"
    }
}, label="POST /auth/register (student)", expected_status=201)

print("\n[1.2] Login with Student Credentials")
status, resp = req("POST", "/auth/login", {
    "email": TEST_EMAIL,
    "password": TEST_PASSWORD
}, label="POST /auth/login (student)", expected_status=200)
if resp and isinstance(resp, dict):
    auth_token = resp.get("access_token")
    if auth_token:
        token_str = str(auth_token)
        clipped_token = "{:.40}".format(token_str)
        print(f"       Token acquired: {clipped_token}...")

print("\n[1.3] Get Current User (auth/me)")
status, resp = req("GET", "/auth/me", token=auth_token, label="GET /auth/me", expected_status=200)
if resp and isinstance(resp, dict):
    STUDENT_ID = resp.get("id")
    print(f"       Student user_id: {STUDENT_ID}")

print("\n[1.4] Token Refresh")
req("POST", "/auth/refresh", token=auth_token, label="POST /auth/refresh", expected_status=200)

print("\n[1.5] Register Faculty Account")
status, resp = req("POST", "/auth/register", {
    "email": TEST_FACULTY_EMAIL,
    "password": TEST_PASSWORD,
    "full_name": "Test Faculty",
    "role": "faculty",
    "profile_data": {
        "employee_id": f"FAC{uuid.uuid4().hex[:6].upper()}",
        "department": "computer_science",
        "designation": "Assistant Professor"
    }
}, label="POST /auth/register (faculty)", expected_status=201)

print("\n[1.6] Login with Faculty Credentials")
status, resp = req("POST", "/auth/login", {
    "email": TEST_FACULTY_EMAIL,
    "password": TEST_PASSWORD
}, label="POST /auth/login (faculty)", expected_status=200)
if resp and isinstance(resp, dict):
    faculty_token = resp.get("access_token")

print("\n[1.7] Logout")
req("POST", "/auth/logout", token=auth_token, label="POST /auth/logout", expected_status=200)

print("\n[1.8] Invalid Login (401 expected)")
req("POST", "/auth/login", {"email": "fake@fake.com", "password": "wrong"}, label="POST /auth/login (invalid creds)", expected_status=401)

# Re-login to get a fresh token for further tests
status, resp = req("POST", "/auth/login", {"email": TEST_EMAIL, "password": TEST_PASSWORD},
    label="POST /auth/login (re-login for next phases)", expected_status=200)
if resp and isinstance(resp, dict):
    auth_token = resp.get("access_token")


# ============================================================
# PHASE 2: Dashboards
# ============================================================
print("\n" + "="*60)
print("PHASE 2 — DASHBOARDS")
print("="*60)

print("\n[2.1] Student Dashboard")
req("GET", "/students/dashboard", token=auth_token, label="GET /students/dashboard", expected_status=200)

print("\n[2.2] Student Profile (me)")
status, resp = req("GET", "/students/me", token=auth_token, label="GET /students/me", expected_status=200)

print("\n[2.3] Faculty Profile (me)")
req("GET", "/faculty/me", token=faculty_token, label="GET /faculty/me", expected_status=200)

print("\n[2.4] Faculty Dashboard")
req("GET", "/faculty/dashboard", token=faculty_token, label="GET /faculty/dashboard", expected_status=200)

print("\n[2.5] Auth Me for Header widget")
req("GET", "/auth/me", token=auth_token, label="GET /auth/me (header widget)", expected_status=200)


# ============================================================
# PHASE 3: Profile Management
# ============================================================
print("\n" + "="*60)
print("PHASE 3 — PROFILE MANAGEMENT")
print("="*60)

print("\n[3.1] Update Student Profile (PATCH /students/me)")
req("PATCH", "/students/me", {
    "cgpa": 8.5,
    "skills": ["Python", "React", "SQL"],
    "preferred_roles": ["Backend Engineer", "Data Engineer"],
    "linkedin_url": "https://linkedin.com/in/testuser",
    "portfolio_url": "https://testuser.dev"
}, token=auth_token, label="PATCH /students/me", expected_status=200)

print("\n[3.2] Get Student Profile Completion")
req("GET", "/students/me/completion", token=auth_token, label="GET /students/me/completion", expected_status=200)

print("\n[3.3] Connect External Platform (LeetCode)")
req("POST", "/students/me/external-platform", {
    "platform": "leetcode",
    "username": "tourist"
}, token=auth_token, label="POST /students/me/external-platform (connect)", expected_status=200)

print("\n[3.4] Disconnect External Platform")
req("DELETE", "/students/me/external-platform?platform=leetcode", token=auth_token,
    label="DELETE /students/me/external-platform", expected_status=200)

print("\n[3.5] Update Faculty Profile")
# Get faculty id first
status, fac_resp = req("GET", "/faculty/me", token=faculty_token, label="GET /faculty/me (for id)", expected_status=200)
FACULTY_ID = fac_resp.get("id") if fac_resp and isinstance(fac_resp, dict) else None
print(f"       Faculty ID: {FACULTY_ID}")
if FACULTY_ID:
    req("PUT", f"/faculty/{FACULTY_ID}", {
        "department": "computer_science",
        "designation": "Associate Professor",
        "office_location": "Block A, Room 101",
        "office_hours": "Mon-Wed 10am-12pm"
    }, token=faculty_token, label="PUT /faculty/{id}", expected_status=200)
else:
    results.append(("PUT /faculty/{id}", "PUT", "SKIPPED", 200, False, "No faculty ID found"))
    print("  ⚠️  SKIP  [PUT /faculty/{id}] → No faculty ID available")


# ============================================================
# PHASE 4: Student Directory & Leaderboard
# ============================================================
print("\n" + "="*60)
print("PHASE 4 — STUDENT DIRECTORY & LEADERBOARD")
print("="*60)

print("\n[4.1] Leaderboard (no filter)")
req("GET", "/students/leaderboard/", token=auth_token, label="GET /students/leaderboard/ (all)", expected_status=200)

print("\n[4.2] Leaderboard with branch filter")
req("GET", "/students/leaderboard/?branch=computer_science", token=auth_token,
    label="GET /students/leaderboard/?branch=computer_science", expected_status=200)

print("\n[4.3] Leaderboard with custom limit")
req("GET", "/students/leaderboard/?limit=10", token=auth_token,
    label="GET /students/leaderboard/?limit=10", expected_status=200)

print("\n[4.4] List Students (paginated)")
req("GET", "/students/?skip=0&limit=20", token=faculty_token, label="GET /students/ (paginated)", expected_status=200)

print("\n[4.5] List Students with filters")
req("GET", "/students/?branch=computer_science&current_year=third", token=faculty_token,
    label="GET /students/?branch&year filter", expected_status=200)

print("\n[4.6] Get Individual Student Detail")
if STUDENT_ID:
    req("GET", f"/students/{STUDENT_ID}", token=faculty_token,
        label="GET /students/{student_id}", expected_status=200)
else:
    results.append(("GET /students/{student_id}", "GET", "SKIPPED", 200, False, "No student ID"))
    print("  ⚠️  SKIP  [GET /students/{student_id}] → No student ID available")


# ============================================================
# PHASE 5: Faculty Management
# ============================================================
print("\n" + "="*60)
print("PHASE 5 — FACULTY MANAGEMENT")
print("="*60)

print("\n[5.1] List Faculty (admin only - expecting 403 for faculty token)")
req("GET", "/faculty/", token=faculty_token, label="GET /faculty/ (faculty token → may be 403)", expected_status=200)

print("\n[5.2] Get Faculty Detail")
if FACULTY_ID:
    req("GET", f"/faculty/{FACULTY_ID}", token=faculty_token,
        label="GET /faculty/{faculty_id}", expected_status=200)
else:
    results.append(("GET /faculty/{faculty_id}", "GET", "SKIPPED", 200, False, "No faculty ID"))
    print("  ⚠️  SKIP  → No faculty ID available")


# ============================================================
# FINAL REPORT TABLE
# ============================================================
print("\n\n" + "="*80)
print("FINAL RESULTS TABLE")
print("="*80)
print(f"{'#':<4} {'Endpoint':<48} {'Method':<8} {'Got':<8} {'Exp':<8} {'Status'}")
print("-"*80)
for i, (label, method, got, exp, ok, err) in enumerate(results, 1):
    status_tag = "✅ PASS" if ok else ("⚠️  SKIP" if got == "SKIPPED" else "❌ FAIL")
    print(f"{i:<4} {label:<48} {method:<8} {str(got):<8} {str(exp):<8} {status_tag}")
    if err and not ok:
        print(f"     ↳ Error: {err}")

total = len(results)
passed = sum(1 for r in results if r[4])
failed = [r for r in results if not r[4] and r[2] != "SKIPPED"]
skipped = [r for r in results if r[2] == "SKIPPED"]
print("-"*80)
print(f"\nTotal: {total}  |  ✅ Passed: {passed}  |  ❌ Failed: {len(failed)}  |  ⚠️  Skipped: {len(skipped)}")

if failed:
    print("\n🔴 FAILED TESTS:")
    for r in failed:
        print(f"  [{r[1]} {r[0]}] → Got {r[2]}, Expected {r[3]}")
        if r[5]:
            print(f"     ↳ {r[5]}")
