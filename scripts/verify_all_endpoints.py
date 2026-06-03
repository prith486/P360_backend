"""
Comprehensive endpoint verification for Placement360 Backend.
Tests all "ready" endpoints from the integration plan.
"""
import requests  # type: ignore
import json
import sys
from datetime import datetime

BASE = "http://localhost:8000"
API = f"{BASE}/api/v1"

STUDENT_MOCK_TOKEN = "mock_valid_student_token_00000000-0000-0000-0000-000000000001"
FACULTY_MOCK_TOKEN = "mock_valid_faculty_token_00000000-0000-0000-0000-000000000002"
INVALID_TOKEN = "totally_invalid_token_xyz"

def hdr(token):
    return {"Authorization": f"Bearer {token}", "Content-Type": "application/json"}

results = {"pass": [], "warn": [], "fail": [], "bug": []}

def check(label, method, url, expected_status, token=None, body=None, params=None, notes=""):
    headers = hdr(token) if token else {"Content-Type": "application/json"}
    try:
        r = getattr(requests, method)(url, json=body, headers=headers, params=params, timeout=10)
        status_ok = r.status_code == expected_status
        try:
            data = r.json()
        except Exception:
            data = r.text

        icon = "✅" if status_ok else "❌"
        result = {
            "label": label,
            "method": method.upper(),
            "url": url,
            "expected": expected_status,
            "got": r.status_code,
            "ok": status_ok,
            "detail": data if not status_ok else None,
            "notes": notes,
        }
        if status_ok:
            results["pass"].append(result)
        else:
            results["fail"].append(result)

        print(f"{icon}  [{r.status_code}] {method.upper()} {url}")
        if not status_ok:
            print(f"     Expected {expected_status}, got {r.status_code}")
            if isinstance(data, dict):
                dumped = str(json.dumps(data, default=str))
                print(f"     Response: {dumped:.300}")
        if notes:
            print(f"     ℹ  {notes}")
        return r.status_code, data
    except requests.exceptions.ConnectionError:
        results["fail"].append({"label": label, "url": url, "error": "CONNECTION_REFUSED"})
        print(f"💥  CONNECTION REFUSED: {method.upper()} {url}")
        return None, None
    except Exception as e:
        results["fail"].append({"label": label, "url": url, "error": str(e)})
        print(f"💥  ERROR: {method.upper()} {url} → {e}")
        return None, None

def warn(label, method, url, expected_status, token=None, body=None, params=None, note=""):
    """Same as check but marks as warning (known limitation) even if it fails."""
    headers = hdr(token) if token else {"Content-Type": "application/json"}
    try:
        r = getattr(requests, method)(url, json=body, headers=headers, params=params, timeout=10)
        try:
            data = r.json()
        except:
            data = r.text
        result = {
            "label": label, "method": method.upper(), "url": url,
            "expected": expected_status, "got": r.status_code,
            "ok": r.status_code == expected_status, "note": note
        }
        results["warn"].append(result)
        icon = "⚠️ " if r.status_code != expected_status else "✅"
        print(f"{icon}  [{r.status_code}] {method.upper()} {url}  ← KNOWN LIMITATION")
        if note:
            print(f"     ℹ  {note}")
        return r.status_code, data
    except Exception as e:
        results["warn"].append({"label": label, "url": url, "error": str(e)})
        print(f"⚠️   ERROR (warn): {e}")
        return None, None


print("\n" + "="*70)
print("  PLACEMENT360 BACKEND — LIVE ENDPOINT VERIFICATION")
print(f"  {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
print("="*70)

# ─────────────────────────────────────────────────────────────────────────────
print("\n📌 PHASE 0: SERVER HEALTH")
# ─────────────────────────────────────────────────────────────────────────────
check("health", "get", f"{BASE}/health", 200)
check("ready", "get", f"{BASE}/ready", 200)
check("live", "get", f"{BASE}/live", 200)
check("metrics", "get", f"{BASE}/metrics", 200)
check("db-health", "get", f"{API}/database/db-health", 200)

# ─────────────────────────────────────────────────────────────────────────────
print("\n📌 PHASE 1: AUTHENTICATION")
# ─────────────────────────────────────────────────────────────────────────────

# 1a. Mock Auth (fast path for UI dev)
print("\n  [1a] Mock Auth endpoints")
_, mock_login = check("mock-login-student", "post", f"{BASE}/api/auth/login", 200,
    body={"email": "student@test.com", "password": "any"})
mock_student_token = mock_login.get("data", {}).get("accessToken", STUDENT_MOCK_TOKEN) if isinstance(mock_login, dict) else STUDENT_MOCK_TOKEN

_, mock_fac_login = check("mock-login-faculty", "post", f"{BASE}/api/auth/login", 200,
    body={"email": "faculty@test.com", "password": "any"})
mock_fac_token = mock_fac_login.get("data", {}).get("accessToken", FACULTY_MOCK_TOKEN) if isinstance(mock_fac_login, dict) else FACULTY_MOCK_TOKEN

check("mock-signup", "post", f"{BASE}/api/auth/signup", 201,
    body={"email": "new@test.com", "password": "pass123", "confirmPassword": "pass123",
          "firstName": "New", "lastName": "User", "role": "student"})
check("mock-me-student", "get", f"{BASE}/api/auth/me", 200, token=STUDENT_MOCK_TOKEN)
check("mock-me-faculty", "get", f"{BASE}/api/auth/me", 200, token=FACULTY_MOCK_TOKEN)
check("mock-logout", "post", f"{BASE}/api/auth/logout", 200)
check("mock-student-dashboard", "get", f"{BASE}/api/student/dashboard", 200, token=STUDENT_MOCK_TOKEN)
check("mock-faculty-dashboard", "get", f"{BASE}/api/faculty/dashboard", 200, token=FACULTY_MOCK_TOKEN)

# 1b. Real Auth (/api/v1/auth/*)
print("\n  [1b] Real Auth endpoints (Supabase)")
check("login-missing-field", "post", f"{API}/auth/login", 422,
    body={"email": "user@test.com"},  # missing password
    notes="Validation: missing password should be 422")

check("login-short-password", "post", f"{API}/auth/login", 422,
    body={"email": "user@test.com", "password": "short"},
    notes="Validation: password < 8 chars should be 422")

check("login-bad-creds", "post", f"{API}/auth/login", 401,
    body={"email": "notexist@test.com", "password": "wrongpass123"},
    notes="Invalid credentials → 401")

check("register-missing-field", "post", f"{API}/auth/register", 422,
    body={"email": "bad"},
    notes="Registration validation should fail")

# Valid me with mock token (goes through real Supabase JWT path unless mock prefix)
check("real-auth-me-with-mock-token", "get", f"{API}/auth/me", 200,
    token=STUDENT_MOCK_TOKEN,
    notes="Mock token bypasses Supabase, reads from DB or mock user")

# No token → 401
check("auth-me-no-token", "get", f"{API}/auth/me", 401,
    notes="No token should return 401 from OAuth2 scheme")

# Invalid token → 401
check("auth-me-invalid-token", "get", f"{API}/auth/me", 401, token=INVALID_TOKEN,
    notes="Bogus token should 401")

# Logout (always returns 200 - intentional stub)
check("logout", "post", f"{API}/auth/logout", 200,
    notes="Logout is client-side only - always 200")

# Refresh (query param, not JSON body)
warn("refresh-no-token", "post", f"{API}/auth/refresh", 401,
    params={"refresh_token": "invalid_refresh_token"},
    note="Refresh with bad token - may return 400 or 401 depending on Supabase")

# ─────────────────────────────────────────────────────────────────────────────
print("\n📌 PHASE 2: DASHBOARD ENDPOINTS")
# ─────────────────────────────────────────────────────────────────────────────

check("student-me-with-mock", "get", f"{API}/students/me", 200,
    token=STUDENT_MOCK_TOKEN,
    notes="Mock student: will either return DB record or 403 if no profile for mock UUID")

check("student-me-no-auth", "get", f"{API}/students/me", 401,
    notes="No token → 401")

check("student-dashboard", "get", f"{API}/students/dashboard", 200,
    token=STUDENT_MOCK_TOKEN,
    notes="Real DB query - may return empty arrays if no data")

check("student-dashboard-pagination", "get", f"{API}/students/dashboard", 200,
    token=STUDENT_MOCK_TOKEN,
    params={"submissionsPage": 1, "submissionsLimit": 3, "assessmentsPage": 1, "assessmentsLimit": 3},
    notes="Pagination params should be accepted")

check("faculty-me", "get", f"{API}/faculty/me", 200,
    token=FACULTY_MOCK_TOKEN,
    notes="Mock faculty: returns mock Faculty object even without DB row")

check("faculty-me-no-auth", "get", f"{API}/faculty/me", 401,
    notes="No token → 401")

check("faculty-dashboard", "get", f"{API}/faculty/dashboard", 200,
    token=FACULTY_MOCK_TOKEN,
    notes="Real DB query - recentActivity will be []")

# Student accessing faculty endpoint → should 403
check("student-accessing-faculty-dashboard", "get", f"{API}/faculty/dashboard", 403,
    token=STUDENT_MOCK_TOKEN,
    notes="Student token should NOT access faculty dashboard - 403 expected")

# ─────────────────────────────────────────────────────────────────────────────
print("\n📌 PHASE 3: PROFILE MANAGEMENT")
# ─────────────────────────────────────────────────────────────────────────────

check("patch-student-me-valid", "patch", f"{API}/students/me", 200,
    token=STUDENT_MOCK_TOKEN,
    body={"skills": ["Python", "FastAPI"], "linkedin_url": "https://linkedin.com/in/test"},
    notes="Partial update - should return updated StudentRead")

check("patch-student-me-invalid-cgpa", "patch", f"{API}/students/me", 422,
    token=STUDENT_MOCK_TOKEN,
    body={"cgpa": "15.0"},  # > 10 is invalid
    notes="CGPA > 10 should fail validation with 422")

check("patch-student-me-ctc-invalid", "patch", f"{API}/students/me", 422,
    token=STUDENT_MOCK_TOKEN,
    body={"expected_ctc_min": "10.00", "expected_ctc_max": "5.00"},  # min > max
    notes="min CTC > max CTC should fail validation")

check("profile-completion", "get", f"{API}/students/me/completion", 200,
    token=STUDENT_MOCK_TOKEN,
    notes="Should return breakdown dict with categories")

check("connect-platform-leetcode", "post", f"{API}/students/me/external-platform", 200,
    token=STUDENT_MOCK_TOKEN,
    body={"platform": "leetcode", "username": "testuser123"},
    notes="Connect LeetCode - saves username, no live fetch")

check("connect-platform-invalid-platform", "post", f"{API}/students/me/external-platform", 422,
    token=STUDENT_MOCK_TOKEN,
    body={"platform": "stackoverflow", "username": "user123"},
    notes="Invalid platform name → 422")

check("connect-platform-bad-username-leetcode", "post", f"{API}/students/me/external-platform", 400,
    token=STUDENT_MOCK_TOKEN,
    body={"platform": "leetcode", "username": "a"},  # too short
    notes="LeetCode usernames need ≥3 chars")

check("disconnect-platform-leetcode", "delete", f"{API}/students/me/external-platform", 200,
    token=STUDENT_MOCK_TOKEN,
    body={"platform": "leetcode"},
    notes="Disconnect LeetCode - clears username and stats")

check("disconnect-invalid-platform", "delete", f"{API}/students/me/external-platform", 422,
    token=STUDENT_MOCK_TOKEN,
    body={"platform": "unknown"},
    notes="Invalid platform → 422")

check("student-me-detailed", "get", f"{API}/students/me/detailed", 200,
    token=STUDENT_MOCK_TOKEN,
    notes="Detailed profile - may have phone attribute mismatch issue")

# faculty update
check("faculty-update-own", "put", f"{API}/faculty/00000000-0000-0000-0000-000000000002", 200,
    token=FACULTY_MOCK_TOKEN,
    body={"department": "Computer Science", "designation": "Professor"},
    notes="Faculty updating own profile by UUID")

# ─────────────────────────────────────────────────────────────────────────────
print("\n📌 PHASE 4: STUDENT DIRECTORY")
# ─────────────────────────────────────────────────────────────────────────────

_, lb = check("leaderboard-default", "get", f"{API}/students/leaderboard/", 200,
    token=STUDENT_MOCK_TOKEN,
    notes="Default leaderboard - top 50 by problems solved")

if lb and isinstance(lb, list):
    print(f"     ℹ  Leaderboard returned {len(lb)} students")

check("leaderboard-with-branch", "get", f"{API}/students/leaderboard/", 200,
    token=STUDENT_MOCK_TOKEN,
    params={"branch": "computer_science", "limit": 10},
    notes="Branch-filtered leaderboard")

check("leaderboard-invalid-branch", "get", f"{API}/students/leaderboard/", 422,
    token=STUDENT_MOCK_TOKEN,
    params={"branch": "invalid_branch"},
    notes="Invalid branch enum should 422")

check("leaderboard-no-auth", "get", f"{API}/students/leaderboard/", 401,
    notes="No token → 401")

# List students (faculty only)
_, students = check("list-students-as-faculty", "get", f"{API}/students/", 200,
    token=FACULTY_MOCK_TOKEN,
    notes="Faculty listing all students")

if students and isinstance(students, list):
    print(f"     ℹ  Found {len(students)} students in DB")

check("list-students-with-skip-limit", "get", f"{API}/students/", 200,
    token=FACULTY_MOCK_TOKEN,
    params={"skip": 0, "limit": 5},
    notes="Paginated student list")

check("list-students-with-branch-filter", "get", f"{API}/students/", 200,
    token=FACULTY_MOCK_TOKEN,
    params={"branch": "computer_science"},
    notes="Filtered by branch")

check("list-students-as-student-should-403", "get", f"{API}/students/", 403,
    token=STUDENT_MOCK_TOKEN,
    notes="Student should NOT list all students - expects 403")

# Get individual student
check("get-student-by-id-invalid-uuid", "get", f"{API}/students/not-a-uuid", 422,
    token=FACULTY_MOCK_TOKEN,
    notes="Invalid UUID format → 422")

check("get-student-nonexistent", "get", f"{API}/students/00000000-0000-0000-0000-999999999999", 404,
    token=FACULTY_MOCK_TOKEN,
    notes="Non-existent student UUID → 404")

check("get-student-as-student-should-403", "get", f"{API}/students/00000000-0000-0000-0000-000000000001", 403,
    token=STUDENT_MOCK_TOKEN,
    notes="Student should NOT call GET /students/{id} - expects 403")

# Create student (admin only)
check("create-student-as-student-should-403", "post", f"{API}/students/", 403,
    token=STUDENT_MOCK_TOKEN,
    body={"user_id": "00000000-0000-0000-0000-000000999001",
          "roll_number": "TEST999", "branch": "computer_science",
          "batch_year": 2024, "current_year": "third"},
    notes="Student creating another student → should 403")

check("create-student-missing-fields", "post", f"{API}/students/", 422,
    token=FACULTY_MOCK_TOKEN,
    body={"roll_number": ""},  # Missing required fields
    notes="Admin creating with missing fields → 422")

# ─────────────────────────────────────────────────────────────────────────────
print("\n📌 PHASE 5: FACULTY MANAGEMENT")
# ─────────────────────────────────────────────────────────────────────────────

check("list-faculty-as-admin", "get", f"{API}/faculty/", 200,
    token=FACULTY_MOCK_TOKEN,  # mock faculty UUID maps to admin in some checks
    notes="Mock faculty UUID (002) is treated as admin in get_current_admin")

check("list-faculty-as-student-should-403", "get", f"{API}/faculty/", 403,
    token=STUDENT_MOCK_TOKEN,
    notes="Student cannot list faculty → 403")

check("get-faculty-by-id-invalid", "get", f"{API}/faculty/not-a-uuid", 422,
    token=FACULTY_MOCK_TOKEN,
    notes="Invalid UUID → 422")

check("get-faculty-nonexistent", "get", f"{API}/faculty/00000000-0000-0000-0000-999999999998", 404,
    token=FACULTY_MOCK_TOKEN,
    notes="Non-existent faculty UUID → 404")

# ─────────────────────────────────────────────────────────────────────────────
print("\n📌 PHASE 6: CORS VERIFICATION")
# ─────────────────────────────────────────────────────────────────────────────
try:
    r = requests.options(f"{API}/auth/login",
        headers={
            "Origin": "http://localhost:3000",
            "Access-Control-Request-Method": "POST",
            "Access-Control-Request-Headers": "Content-Type,Authorization"
        }, timeout=5)
    acao = r.headers.get("access-control-allow-origin", "MISSING")
    acam = r.headers.get("access-control-allow-methods", "MISSING")
    acah = r.headers.get("access-control-allow-headers", "MISSING")
    acac = r.headers.get("access-control-allow-credentials", "MISSING")
    cors_ok = acao in ["http://localhost:3000", "*"]
    icon = "✅" if cors_ok else "❌"
    print(f"\n{icon}  CORS Preflight Check")
    print(f"     Allow-Origin:       {acao}")
    print(f"     Allow-Methods:      {acam}")
    print(f"     Allow-Headers:      {acah}")
    print(f"     Allow-Credentials:  {acac}")
    results["pass" if cors_ok else "fail"].append({"label": "cors-preflight", "ok": cors_ok, "origin": acao})
except Exception as e:
    print(f"❌  CORS check failed: {e}")
    results["fail"].append({"label": "cors-preflight", "error": str(e)})

# ─────────────────────────────────────────────────────────────────────────────
print("\n📌 PHASE 7: KNOWN STUBS (Expect 404/405)")
# ─────────────────────────────────────────────────────────────────────────────
stub_endpoints = [
    ("get", f"{API}/assessments/", "Assessments - STUB"),
    ("get", f"{API}/questions/", "Questions - STUB"),
    ("get", f"{API}/submissions/", "Submissions - STUB"),
    ("get", f"{API}/platforms/", "External Platforms direct router - STUB"),
    ("get", f"{API}/analytics/", "Analytics - STUB"),
    ("get", f"{API}/companies/", "Companies - STUB"),
    ("post", f"{API}/ai/feedback", "AI Feedback - STUB"),
]
for method, url, label in stub_endpoints:
    try:
        r = getattr(requests, method)(url, headers=hdr(FACULTY_MOCK_TOKEN), timeout=5)
        print(f"  [{r.status_code}] {label} → {url}")
        results["warn"].append({"label": label, "status": r.status_code, "note": "stub endpoint"})
    except Exception:
        print(f"  [ERR] {label} → connection error")

# ─────────────────────────────────────────────────────────────────────────────
print("\n📌 PHASE 8: DATABASE STATE CHECK")
# ─────────────────────────────────────────────────────────────────────────────
try:
    r = requests.get(f"{API}/database/db-health", timeout=10)
    data = r.json()
    print(f"\n✅  DB Health: {data.get('status')} | Latency: {data.get('latency_ms')}ms")
    results["pass"].append({"label": "db-health-state", "latency_ms": data.get("latency_ms")})
except Exception as e:
    print(f"❌  DB Health check failed: {e}")
    results["fail"].append({"label": "db-health-state", "error": str(e)})

# ─────────────────────────────────────────────────────────────────────────────
print("\n" + "="*70)
print("  SUMMARY")
print("="*70)
total = len(results["pass"]) + len(results["fail"])
print(f"  ✅ PASS:    {len(results['pass'])}/{total}")
print(f"  ❌ FAIL:    {len(results['fail'])}/{total}")
print(f"  ⚠️  WARN:    {len(results['warn'])} (known limitations or stubs)")
print()

if results["fail"]:
    print("FAILED TESTS:")
    for r in results["fail"]:
        exp = r.get('expected', '?')
        got = r.get('got', r.get('error', '?'))
        print(f"  ❌ {r.get('label','?')} — expected {exp}, got {got}")
        if r.get("detail"):
            dumped = str(json.dumps(r["detail"], default=str))
            print(f"      Detail: {dumped:.200}")

print()
# Save results to file
with open("scripts/verification_results.json", "w") as f:
    json.dump(results, f, indent=2, default=str)
print("  📄 Full results saved to scripts/verification_results.json")
print("="*70)
