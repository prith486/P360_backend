"""
Focused quick-test: Tests only endpoints that use mock tokens (fast, no Supabase timeout).
Skips any endpoints that call Supabase Auth (login with real creds, etc.)
"""
import requests, json  # type: ignore
from datetime import datetime

BASE = "http://localhost:8000"
API = f"{BASE}/api/v1"

STUDENT_TOKEN = "mock_valid_student_token_00000000-0000-0000-0000-000000000001"
FACULTY_TOKEN = "mock_valid_faculty_token_00000000-0000-0000-0000-000000000002"

def hdr(token=None):
    h = {"Content-Type": "application/json"}
    if token:
        h["Authorization"] = f"Bearer {token}"
    return h

results = []

def t(label, method, url, exp, token=None, body=None, params=None, note=""):
    try:
        r = getattr(requests, method)(url, json=body, headers=hdr(token), params=params, timeout=8)
        ok = r.status_code == exp
        try:
            data = r.json()
        except:
            temp_text = str(r.text)
            data = f"{temp_text:.200}"
        results.append({"ok": ok, "label": label, "got": r.status_code, "exp": exp})
        icon = "✅" if ok else "❌"
        print(f"{icon} [{r.status_code:3d}] {label}")
        if not ok:
            detail = str(data)
            clipped = f"{detail:.250}"
            print(f"       Expected {exp} | {clipped}")
        if note and not ok:
            print(f"       Note: {note}")
        return r.status_code, data
    except requests.exceptions.Timeout:
        results.append({"ok": False, "label": label, "got": "TIMEOUT", "exp": exp})
        print(f"⏱️ [TMO] {label} — TIMED OUT (Supabase call?)")
        return "TIMEOUT", None
    except Exception as e:
        results.append({"ok": False, "label": label, "got": "ERR", "exp": exp})
        err_str = str(e)
        clipped_err = f"{err_str:.100}"
        print(f"💥 [ERR] {label} — {clipped_err}")
        return "ERR", None

print("\n" + "="*65)
print("  PLACEMENT360 — FOCUSED LIVE VERIFICATION")
print(f"  {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
print("="*65)

# ── HEALTH (correct paths) ────────────────────────────────────────
print("\n🔷 HEALTH ENDPOINTS")
t("GET /api/v1/health",   "get", f"{API}/health",   200)
t("GET /api/v1/ready",    "get", f"{API}/ready",    200)
t("GET /api/v1/live",     "get", f"{API}/live",     200)
t("GET /api/v1/metrics",  "get", f"{API}/metrics",  200)
t("GET /database/db-health", "get", f"{API}/database/db-health", 200)
t("GET /database/db-info",   "get", f"{API}/database/db-info",   200)

# ROOT
t("GET / (root)", "get", f"{BASE}/", 200)

# ── MOCK AUTH ─────────────────────────────────────────────────────
print("\n🔷 MOCK AUTH ENDPOINTS (/api/auth/*)")
t("Mock login student",  "post", f"{BASE}/api/auth/login",  200, body={"email":"s@test.com","password":"x"})
_, ml = t("Mock login faculty",  "post", f"{BASE}/api/auth/login",  200, body={"email":"faculty@test.com","password":"x"})
t("Mock signup",          "post", f"{BASE}/api/auth/signup", 201, body={"email":"n@t.com","password":"abc","confirmPassword":"abc","firstName":"A","lastName":"B","role":"student"})
t("Mock GET /api/auth/me (student)", "get", f"{BASE}/api/auth/me", 200, token=STUDENT_TOKEN)
t("Mock GET /api/auth/me (faculty)", "get", f"{BASE}/api/auth/me", 200, token=FACULTY_TOKEN)
t("Mock logout",          "post", f"{BASE}/api/auth/logout", 200)
t("Mock student dashboard", "get", f"{BASE}/api/student/dashboard", 200, token=STUDENT_TOKEN)
t("Mock faculty dashboard", "get", f"{BASE}/api/faculty/dashboard", 200, token=FACULTY_TOKEN)

# ── REAL AUTH (no Supabase calls needed: mock tokens bypass it) ───
print("\n🔷 REAL AUTH /api/v1/auth/*")
t("GET /auth/me (mock student token)", "get", f"{API}/auth/me", 200, token=STUDENT_TOKEN)
t("GET /auth/me (no token → 401)",     "get", f"{API}/auth/me", 401)
t("GET /auth/me (invalid token → 401)","get", f"{API}/auth/me", 401, token="bad_token_xyz")
t("POST /auth/logout",                 "post", f"{API}/auth/logout", 200)
# Validate-only tests (no Supabase call)
t("POST /auth/login missing password → 422", "post", f"{API}/auth/login", 422,
  body={"email": "user@test.com"})
t("POST /auth/login short password → 422",   "post", f"{API}/auth/login", 422,
  body={"email": "user@test.com", "password": "short"})
t("POST /auth/register missing all → 422",   "post", f"{API}/auth/register", 422,
  body={"email": "bad"})

# ── STUDENT ENDPOINTS ──────────────────────────────────────────────
print("\n🔷 STUDENT ENDPOINTS /api/v1/students/*")
t("GET /students/me (mock student)", "get", f"{API}/students/me", 200, token=STUDENT_TOKEN,
  note="Mock student UUID needs a DB row to return 200; else returns 403")
t("GET /students/me (no token → 401)", "get", f"{API}/students/me", 401)
t("GET /students/me/detailed", "get", f"{API}/students/me/detailed", 200, token=STUDENT_TOKEN)
t("GET /students/me/completion", "get", f"{API}/students/me/completion", 200, token=STUDENT_TOKEN)

# Dashboard
t("GET /students/dashboard (mock student)", "get", f"{API}/students/dashboard", 200, token=STUDENT_TOKEN)
t("GET /students/dashboard (paginated)", "get", f"{API}/students/dashboard", 200, token=STUDENT_TOKEN,
  params={"submissionsPage":1,"submissionsLimit":3})

# Platform connect/disconnect
t("POST /students/me/external-platform leetcode valid",  "post", f"{API}/students/me/external-platform", 200,
  token=STUDENT_TOKEN, body={"platform":"leetcode","username":"testuser123"})
t("POST /students/me/external-platform invalid-platform", "post", f"{API}/students/me/external-platform", 422,
  token=STUDENT_TOKEN, body={"platform":"stackoverflow","username":"user"})
t("POST /students/me/external-platform bad username (1 char)", "post", f"{API}/students/me/external-platform", 400,
  token=STUDENT_TOKEN, body={"platform":"leetcode","username":"a"})
t("DELETE /students/me/external-platform leetcode", "delete", f"{API}/students/me/external-platform", 200,
  token=STUDENT_TOKEN, body={"platform":"leetcode"})
t("DELETE /students/me/external-platform invalid", "delete", f"{API}/students/me/external-platform", 422,
  token=STUDENT_TOKEN, body={"platform":"noexist"})

# PATCH student
t("PATCH /students/me valid",    "patch", f"{API}/students/me", 200, token=STUDENT_TOKEN,
  body={"skills":["Python"],"linkedin_url":"https://linkedin.com/in/x"})
t("PATCH /students/me bad cgpa", "patch", f"{API}/students/me", 422, token=STUDENT_TOKEN,
  body={"cgpa":"15.0"})

# Leaderboard
_, lb = t("GET /students/leaderboard/ (auth)", "get", f"{API}/students/leaderboard/", 200, token=STUDENT_TOKEN)
if isinstance(lb, list):
    print(f"       ℹ  Leaderboard has {len(lb)} students")
t("GET /students/leaderboard/ (no auth → 401)", "get", f"{API}/students/leaderboard/", 401)
t("GET /students/leaderboard/ (branch filter)", "get", f"{API}/students/leaderboard/", 200,
  token=STUDENT_TOKEN, params={"branch":"computer_science","limit":5})
t("GET /students/leaderboard/ (invalid branch → 422)", "get", f"{API}/students/leaderboard/", 422,
  token=STUDENT_TOKEN, params={"branch":"invalid_branch"})

# List students (faculty only)
_, studs = t("GET /students/ (faculty → 200)", "get", f"{API}/students/", 200, token=FACULTY_TOKEN)
if isinstance(studs, list):
    print(f"       ℹ  Total students in DB: {len(studs)}")
t("GET /students/ (student → 403)", "get", f"{API}/students/", 403, token=STUDENT_TOKEN)
t("GET /students/ (no auth → 401)", "get", f"{API}/students/", 401)
t("GET /students/ (skip/limit)", "get", f"{API}/students/", 200, token=FACULTY_TOKEN,
  params={"skip":0,"limit":5})
t("GET /students/ (branch filter)", "get", f"{API}/students/", 200, token=FACULTY_TOKEN,
  params={"branch":"computer_science"})

# Student by ID
t("GET /students/{invalid_uuid} → 422", "get", f"{API}/students/not-a-valid-uuid", 422, token=FACULTY_TOKEN)
t("GET /students/{nonexistent} → 404",  "get", f"{API}/students/00000000-0000-0000-0000-999999999999", 404, token=FACULTY_TOKEN)
t("GET /students/{id} (student → 403)", "get", f"{API}/students/00000000-0000-0000-0000-000000000001", 403, token=STUDENT_TOKEN)

# Create student (admin only → faculty mock UUID acts as admin check)
t("POST /students/ (missing fields → 422)", "post", f"{API}/students/", 422, token=FACULTY_TOKEN,
  body={"roll_number":""})

# ── ROUTE ORDER BUG CHECK ─────────────────────────────────────────
print("\n🔷 ROUTE ORDERING BUG CHECK (dashboard vs /{id})")
# The key bug: does /dashboard get caught by /{student_id} route?
s, d = t("GET /students/dashboard (route-order check)", "get", f"{API}/students/dashboard", 200, token=STUDENT_TOKEN)
if s == 422 and isinstance(d, dict):
    errs = d.get("errors", d.get("detail", ""))
    if "uuid" in str(errs).lower():
        print("       🐛 BUG CONFIRMED: /dashboard treated as UUID path param!")
        results.append({"ok": False, "label": "ROUTE_ORDER_BUG", "got": "422-UUID", "exp": 200})

# ── FACULTY ENDPOINTS ─────────────────────────────────────────────
print("\n🔷 FACULTY ENDPOINTS /api/v1/faculty/*")
t("GET /faculty/me (faculty)", "get", f"{API}/faculty/me", 200, token=FACULTY_TOKEN)
t("GET /faculty/me (no auth → 401)", "get", f"{API}/faculty/me", 401)
t("GET /faculty/me (student → 403  or 500)", "get", f"{API}/faculty/me", 403, token=STUDENT_TOKEN,
  note="Student has no faculty profile → should be 403")
t("GET /faculty/dashboard (faculty)", "get", f"{API}/faculty/dashboard", 200, token=FACULTY_TOKEN)
t("GET /faculty/ (admin only)", "get", f"{API}/faculty/", 200, token=FACULTY_TOKEN)
t("GET /faculty/ (student → 403)", "get", f"{API}/faculty/", 403, token=STUDENT_TOKEN)
t("GET /faculty/{invalid_uuid} → 422", "get", f"{API}/faculty/not-a-uuid", 422, token=FACULTY_TOKEN)
t("GET /faculty/{nonexistent} → 404",  "get", f"{API}/faculty/00000000-0000-0000-0000-999999999998", 404, token=FACULTY_TOKEN)
# Faculty update own profile
t("PUT /faculty/{id} own profile", "put", f"{API}/faculty/00000000-0000-0000-0000-000000000002", 200,
  token=FACULTY_TOKEN, body={"department":"CS","designation":"Prof"})

# ── STUBS ─────────────────────────────────────────────────────────
print("\n🔷 STUB ENDPOINTS (all should return 404 or 405 — no routes defined)")
for method, url, label in [
    ("get",  f"{API}/assessments/",    "assessments"),
    ("get",  f"{API}/questions/",      "questions"),
    ("get",  f"{API}/submissions/",    "submissions"),
    ("get",  f"{API}/platforms/",      "platforms"),
    ("get",  f"{API}/analytics/",      "analytics"),
    ("get",  f"{API}/companies/",      "companies"),
    ("post", f"{API}/ai/feedback",     "ai-feedback"),
]:
    try:
        r = getattr(requests, method)(url, headers=hdr(FACULTY_TOKEN), timeout=5)
        print(f"  [{r.status_code}] {label} — {url}")
    except Exception as e:
        print(f"  [ERR] {label} — {e}")

# ── CORS ──────────────────────────────────────────────────────────
print("\n🔷 CORS PREFLIGHT CHECK")
try:
    r = requests.options(f"{API}/auth/login",
        headers={"Origin":"http://localhost:3000",
                 "Access-Control-Request-Method":"POST",
                 "Access-Control-Request-Headers":"Content-Type,Authorization"},
        timeout=5)
    acao = r.headers.get("access-control-allow-origin","MISSING")
    acac = r.headers.get("access-control-allow-credentials","MISSING")
    acam = r.headers.get("access-control-allow-methods","MISSING")
    ok = acao in ["http://localhost:3000","*"]
    icon = "✅" if ok else "❌"
    print(f"{icon} CORS Allow-Origin:       {acao}")
    print(f"   CORS Allow-Credentials: {acac}")
    print(f"   CORS Allow-Methods:     {acam}")
    results.append({"ok":ok,"label":"CORS","got":acao,"exp":"http://localhost:3000"})
except Exception as e:
    print(f"❌ CORS check failed: {e}")

# ── SUMMARY ───────────────────────────────────────────────────────
pass_c  = sum(1 for r in results if r["ok"])
fail_c  = sum(1 for r in results if not r["ok"])
total_c = len(results)

print("\n" + "="*65)
print(f"  RESULTS: {pass_c} PASS  /  {fail_c} FAIL  /  {total_c} TOTAL")
print("="*65)
if fail_c:
    print("\nFAILED:")
    for r in results:
        if not r["ok"]:
            print(f"  ❌  {r['label']}  →  expected {r['exp']}, got {r['got']}")

with open("scripts/quick_verification_results.json","w") as f:
    json.dump(results,f,indent=2,default=str)
print("\n  Full results → scripts/quick_verification_results.json")
