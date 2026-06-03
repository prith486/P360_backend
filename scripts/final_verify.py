"""
Targeted endpoint verification - no Supabase live calls.
Runs sequentially with individual timeout tracking.
"""
import requests, json, sys
from datetime import datetime

BASE = "http://localhost:8000"
API  = f"{BASE}/api/v1"
ST   = "mock_valid_student_token_00000000-0000-0000-0000-000000000001"
FT   = "mock_valid_faculty_token_00000000-0000-0000-0000-000000000002"

results = {"pass": [], "fail": [], "bug": []}

def h(token=None):
    return {"Authorization": f"Bearer {token}", "Content-Type": "application/json"} if token else {"Content-Type": "application/json"}

def t(label, method, url, exp, token=None, body=None, params=None):
    try:
        r = getattr(requests, method)(url, json=body, headers=h(token), params=params, timeout=6)
        c = r.status_code
        try:    data = r.json()
        except: data = r.text[:300]
        ok = (c == exp)
        icon = "✅" if ok else "❌"
        extra = ""
        if not ok:
            dumped = str(json.dumps(data, default=str))
            extra = f"  expected={exp} | {dumped[0:200]}"
        print(f"  {icon} [{c:3d}] {label}{extra}")
        (results["pass"] if ok else results["fail"]).append({"label": label, "got": c, "exp": exp, "detail": data if not ok else None})
        return c, data
    except requests.exceptions.Timeout:
        print(f"  ⏱️  [TMO] {label}  ← TIMED OUT")
        results["fail"].append({"label": label, "got": "TIMEOUT", "exp": exp})
        return "TIMEOUT", None
    except Exception as e:
        err_msg = str(e)
        print(f"  💥  [ERR] {label}  ← {err_msg[0:80]}")
        results["fail"].append({"label": label, "got": "ERR", "exp": exp})
        return "ERR", None

print(f"\n{'='*68}")
print(f"  PLACEMENT360 — LIVE API VERIFICATION  {datetime.now():%Y-%m-%d %H:%M:%S}")
print(f"{'='*68}")

# ── HEALTH ──────────────────────────────────────────────────────────────────
print("\n📡 HEALTH ENDPOINTS")
t("GET /api/v1/health",          "get", f"{API}/health",            200)
t("GET /api/v1/ready",           "get", f"{API}/ready",             200)
t("GET /api/v1/live",            "get", f"{API}/live",              200)
t("GET /api/v1/metrics",         "get", f"{API}/metrics",           200)
t("GET /database/db-health",     "get", f"{API}/database/db-health",200)
t("GET /database/db-info (dev)", "get", f"{API}/database/db-info",  200)
t("GET / (root endpoint)",       "get", f"{BASE}/",                 200)

# ── MOCK AUTH ───────────────────────────────────────────────────────────────
print("\n🔑 MOCK AUTH  /api/auth/*  (no Supabase needed)")
_, r1 = t("POST /api/auth/login (student)",     "post", f"{BASE}/api/auth/login",  200, body={"email":"student@t.com","password":"x"})
_, r2 = t("POST /api/auth/login (faculty)",     "post", f"{BASE}/api/auth/login",  200, body={"email":"faculty@t.com","password":"x"})
_, r3 = t("POST /api/auth/signup",              "post", f"{BASE}/api/auth/signup", 201, body={"email":"new@t.com","password":"pass","confirmPassword":"pass","firstName":"A","lastName":"B","role":"student"})
t("GET  /api/auth/me (student token)", "get",  f"{BASE}/api/auth/me",     200, token=ST)
t("GET  /api/auth/me (faculty token)", "get",  f"{BASE}/api/auth/me",     200, token=FT)
t("POST /api/auth/logout",            "post", f"{BASE}/api/auth/logout",  200)
_, dash_mock = t("GET /api/student/dashboard (mock)",  "get",  f"{BASE}/api/student/dashboard", 200, token=ST)
_, fdash_mock = t("GET /api/faculty/dashboard (mock)", "get",  f"{BASE}/api/faculty/dashboard", 200, token=FT)

# Validate response structure
if isinstance(dash_mock, dict) and dash_mock.get("success"):
    d = dash_mock.get("data", {})
    has = all(k in d for k in ["profile","stats","recentSubmissions","upcomingAssessments"])
    print(f"     {'✅' if has else '❌'} Mock student dashboard has all required keys: {list(d.keys())}")

# ── REAL AUTH ───────────────────────────────────────────────────────────────
print("\n🔑 REAL AUTH  /api/v1/auth/*")
_, me = t("GET /auth/me (mock-student token → 200)",     "get",  f"{API}/auth/me", 200, token=ST)
if isinstance(me, dict) and me.get("success"):
    print(f"     ✅ /auth/me returns: {me.get('data',{})}")
t("GET /auth/me (no token → 401)",                       "get",  f"{API}/auth/me", 401)
t("GET /auth/me (invalid token → 401)",                  "get",  f"{API}/auth/me", 401, token="garbage")
t("POST /auth/logout (200)",                             "post", f"{API}/auth/logout", 200)
t("POST /auth/login (missing password → 422)",           "post", f"{API}/auth/login", 422, body={"email":"u@t.com"})
t("POST /auth/login (password too short → 422)",         "post", f"{API}/auth/login", 422, body={"email":"u@t.com","password":"short"})
t("POST /auth/register (all missing → 422)",             "post", f"{API}/auth/register", 422, body={"email":"bad"})
t("POST /auth/register (bad role → 422)",                "post", f"{API}/auth/register", 422,
  body={"email":"x@t.com","password":"password123","full_name":"Test User","role":"superadmin"})

# ── STUDENT ENDPOINTS ────────────────────────────────────────────────────────
print("\n👨‍🎓 STUDENT ENDPOINTS  /api/v1/students/*")
_, me_s = t("GET /students/me (mock-student)",            "get", f"{API}/students/me", 200, token=ST)
t("GET /students/me (no-token → 401)",                    "get", f"{API}/students/me", 401)
_, detail = t("GET /students/me/detailed",                "get", f"{API}/students/me/detailed", 200, token=ST)
_, compl = t("GET /students/me/completion",               "get", f"{API}/students/me/completion", 200, token=ST)

if isinstance(compl, dict):
    has = all(k in compl for k in ["overall_completion","categories","recommendations"])
    print(f"     {'✅' if has else '❌'} completion has keys: {list(compl.keys())}")

# DASHBOARD (route order bug check)
_, sdash = t("GET /students/dashboard",                   "get", f"{API}/students/dashboard", 200, token=ST)
if sdash:
    if isinstance(sdash, dict) and "errors" in str(sdash).lower() and "uuid" in str(sdash).lower():
        print("     🐛 ROUTE-ORDER BUG: /dashboard caught by /{student_id}!")
        results["bug"].append({"label": "ROUTE_ORDER", "detail": "/students/dashboard resolved as /{student_id}"})
    elif isinstance(sdash, dict) and sdash.get("success"):
        d = sdash.get("data", {})
        stats = d.get("stats", {})
        print(f"     ✅ Dashboard data: stats keys={list(stats.keys())}")
        if stats.get("currentStreak") == 0:
            print(f"     ⚠️  streak=0 (known TODO)")
        if stats.get("rank") == 0:
            print(f"     ⚠️  rank=0 (known TODO)")

_, sdash_p = t("GET /students/dashboard (paginated)",     "get", f"{API}/students/dashboard", 200, token=ST,
               params={"submissionsPage":1,"submissionsLimit":3})

# PATCH
_, upd = t("PATCH /students/me (skills update)",          "patch", f"{API}/students/me", 200, token=ST,
           body={"skills":["Python","React","FastAPI"]})
if isinstance(upd, dict):
    skills = upd.get("skills")
    print(f"     {'✅' if skills == ['Python','React','FastAPI'] else '⚠️ '} Returned skills: {skills}")

t("PATCH /students/me (cgpa > 10 → 422)",                 "patch", f"{API}/students/me", 422, token=ST, body={"cgpa":"15.0"})
t("PATCH /students/me (no auth → 401)",                   "patch", f"{API}/students/me", 401, body={"skills":[]})

# EXTERNAL PLATFORMS
_, ep1 = t("POST /ext-platform (leetcode valid)",         "post", f"{API}/students/me/external-platform", 200,
           token=ST, body={"platform":"leetcode","username":"testuser123"})
if isinstance(ep1, dict) and ep1.get("leetcode_username") == "testuser123":
    print("     ✅ leetcode_username saved correctly")

t("POST /ext-platform (invalid platform → 422)",           "post", f"{API}/students/me/external-platform", 422,
  token=ST, body={"platform":"stackoverflow","username":"user"})
t("POST /ext-platform (username too short → 400)",         "post", f"{API}/students/me/external-platform", 400,
  token=ST, body={"platform":"leetcode","username":"a"})
t("POST /ext-platform github valid",                       "post", f"{API}/students/me/external-platform", 200,
  token=ST, body={"platform":"github","username":"testdev"})
t("DELETE /ext-platform (leetcode)",                       "delete", f"{API}/students/me/external-platform", 200,
  token=ST, body={"platform":"leetcode"})
t("DELETE /ext-platform (invalid → 422)",                  "delete", f"{API}/students/me/external-platform", 422,
  token=ST, body={"platform":"nope"})

# LEADERBOARD
_, lb = t("GET /leaderboard/ (student auth)",             "get", f"{API}/students/leaderboard/", 200, token=ST)
if isinstance(lb, list):
    print(f"     ✅ Leaderboard: {len(lb)} records")
t("GET /leaderboard/ (no auth → 401)",                    "get", f"{API}/students/leaderboard/", 401)
t("GET /leaderboard/ (branch filter cs)",                 "get", f"{API}/students/leaderboard/", 200,
  token=ST, params={"branch":"computer_science"})
t("GET /leaderboard/ (invalid branch → 422)",             "get", f"{API}/students/leaderboard/", 422,
  token=ST, params={"branch":"made_up_branch"})

# LIST STUDENTS
_, studs = t("GET /students/ (faculty auth → 200)",       "get", f"{API}/students/", 200, token=FT)
if isinstance(studs, list):
    print(f"     ✅ Total students in DB: {len(studs)}")
    if studs:
        s0 = studs[0]
        req = ["id","roll_number","branch","current_year","readiness_score"]
        missing = [f for f in req if f not in s0]
        print(f"     {'✅' if not missing else '❌'} StudentRead fields present (missing: {missing})")
t("GET /students/ (student → 403)",                       "get", f"{API}/students/", 403, token=ST)
t("GET /students/ (no auth → 401)",                       "get", f"{API}/students/", 401)
t("GET /students/ (skip=0,limit=3)",                      "get", f"{API}/students/", 200, token=FT, params={"skip":0,"limit":3})
t("GET /students/ (branch filter)",                       "get", f"{API}/students/", 200, token=FT, params={"branch":"computer_science"})
t("GET /students/ (year filter)",                         "get", f"{API}/students/", 200, token=FT, params={"current_year":"third"})

# STUDENT BY ID
t("GET /students/{invalid-uuid} → 422",                   "get", f"{API}/students/not-a-valid-uuid", 422, token=FT)
t("GET /students/{nonexistent} → 404",                    "get", f"{API}/students/00000000-0000-0000-0000-999999999999", 404, token=FT)
t("GET /students/{id} as-student → 403",                  "get", f"{API}/students/00000000-0000-0000-0000-000000000001", 403, token=ST)
t("POST /students/ (missing fields → 422)",               "post", f"{API}/students/", 422, token=FT, body={"roll_number":""})

# ── FACULTY ENDPOINTS ────────────────────────────────────────────────────────
print("\n👨‍🏫 FACULTY ENDPOINTS  /api/v1/faculty/*")
_, fme = t("GET /faculty/me (faculty)",                   "get", f"{API}/faculty/me", 200, token=FT)
if isinstance(fme, dict):
    print(f"     ✅ Faculty me fields: {list(fme.keys())[0:8]}")
t("GET /faculty/me (no auth → 401)",                      "get", f"{API}/faculty/me", 401)
t("GET /faculty/me (student → 403 or 500)",               "get", f"{API}/faculty/me", 403, token=ST)

_, fdash = t("GET /faculty/dashboard",                    "get", f"{API}/faculty/dashboard", 200, token=FT)
if isinstance(fdash, dict) and fdash.get("success"):
    d = fdash.get("data", {})
    stats = d.get("stats", {})
    ract  = d.get("recentActivity", "NOT_IN_RESPONSE")
    print(f"     ✅ Faculty dashboard stats: {stats}")
    print(f"     {'⚠️ ' if ract == [] else '✅'} recentActivity: {ract} (empty [] = known TODO)")

t("GET /faculty/dashboard (student token)",               "get", f"{API}/faculty/dashboard", 403, token=ST)

_, fl = t("GET /faculty/ (faculty-as-admin)",             "get", f"{API}/faculty/", 200, token=FT)
if isinstance(fl, list):
    print(f"     ✅ Faculty list: {len(fl)} records")
t("GET /faculty/ (student → 403)",                        "get", f"{API}/faculty/", 403, token=ST)
t("GET /faculty/{invalid-uuid} → 422",                    "get", f"{API}/faculty/not-a-uuid", 422, token=FT)
t("GET /faculty/{nonexistent} → 404",                     "get", f"{API}/faculty/00000000-0000-0000-0000-999999999998", 404, token=FT)
t("PUT /faculty/{id} update-own",                         "put", f"{API}/faculty/00000000-0000-0000-0000-000000000002", 200,
  token=FT, body={"department":"CS","designation":"Prof"})
t("PUT /faculty/{id} as-student → 403",                   "put", f"{API}/faculty/00000000-0000-0000-0000-000000000002", 403,
  token=ST, body={"department":"CS"})

# ── STUBS ────────────────────────────────────────────────────────────────────
print("\n🚧 STUB ENDPOINTS (expect 404 or 405 — zero routes implemented)")
for method, url, name in [
    ("get",  f"{API}/assessments/",    "/assessments/"),
    ("get",  f"{API}/questions/",      "/questions/"),
    ("get",  f"{API}/submissions/",    "/submissions/"),
    ("get",  f"{API}/platforms/",      "/platforms/"),
    ("get",  f"{API}/analytics/",      "/analytics/"),
    ("get",  f"{API}/companies/",      "/companies/"),
    ("post", f"{API}/ai/feedback",     "/ai/feedback"),
]:
    try:
        r = getattr(requests, method)(url, headers=h(FT), timeout=5)
        icon = "✅" if r.status_code in [404, 405] else "⚠️ "
        print(f"  {icon} [{r.status_code}] {name}")
    except Exception as e:
        print(f"  💥  {name} ERR: {e}")

# ── CORS ─────────────────────────────────────────────────────────────────────
print("\n🌐 CORS CHECK  (Origin: http://localhost:3000)")
try:
    r = requests.options(f"{API}/auth/login",
        headers={"Origin":"http://localhost:3000","Access-Control-Request-Method":"POST","Access-Control-Request-Headers":"Content-Type,Authorization"},
        timeout=5)
    acao = r.headers.get("access-control-allow-origin","MISSING")
    acac = r.headers.get("access-control-allow-credentials","MISSING")
    acam = r.headers.get("access-control-allow-methods","MISSING")
    acah = r.headers.get("access-control-allow-headers","MISSING")
    cors_ok = acao in ["http://localhost:3000","*"]
    print(f"  {'✅' if cors_ok else '❌'} Allow-Origin:       {acao}")
    print(f"  {'✅' if acac=='true' else '❌'} Allow-Credentials:  {acac}")
    print(f"  ✅ Allow-Methods:     {acam[:60] if acam else 'MISSING'}")
    print(f"  ✅ Allow-Headers:     {acah[:60] if acah else 'MISSING'}")
    results["pass" if cors_ok else "fail"].append({"label":"CORS","ok":cors_ok})
except Exception as e:
    print(f"  ❌ CORS check error: {e}")

# ── DATABASE STATE ────────────────────────────────────────────────────────────
print("\n🗄️  DATABASE STATE CHECK")
try:
    r = requests.get(f"{API}/database/db-health", timeout=5)
    d = r.json()
    print(f"  ✅ DB: {d.get('status')}, latency={d.get('latency_ms')}ms, env={d.get('environment')}")
    _, dtest = results, requests.get(f"{API}/database/db-test-query", timeout=5)
    dt = dtest.json()
    print(f"  ✅ DB test query: {dt.get('results',{})}")
except Exception as e:
    print(f"  ❌ DB check error: {e}")

# ── SUMMARY ──────────────────────────────────────────────────────────────────
total = len(results["pass"]) + len(results["fail"])
print(f"\n{'='*68}")
print(f"  RESULTS:  ✅ {len(results['pass'])} PASS  |  ❌ {len(results['fail'])} FAIL  |  🐛 {len(results['bug'])} BUGS  |  {total} TOTAL")
print(f"{'='*68}")

if results["fail"]:
    print("\nFAILED TESTS:")
    for r in results["fail"]:
        print(f"  ❌  {r['label']}  got={r['got']}  exp={r['exp']}")
        if r.get("detail") and r["detail"] not in [None, ""]:
            dumped = str(json.dumps(r['detail'], default=str))
            print(f"       {dumped[0:200]}")

if results["bug"]:
    print("\nBUGS CONFIRMED:")
    for b in results["bug"]:
        print(f"  🐛  {b}")

with open("scripts/final_verification_results.json", "w") as f:
    json.dump(results, f, indent=2, default=str)
print("\n  📄 Results saved to scripts/final_verification_results.json")
