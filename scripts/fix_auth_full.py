import os, requests, sys
from dotenv import load_dotenv

# Use absolute path to .env if needed, but normally load_dotenv() works in CWD
load_dotenv()

SUPABASE_URL = os.getenv("SUPABASE_URL")
SERVICE_KEY = os.getenv("SUPABASE_SERVICE_ROLE_KEY")
ANON_KEY = os.getenv("SUPABASE_ANON_KEY")
BASE = "http://localhost:8000/api/v1"

headers_admin = {
    "apikey": SERVICE_KEY,
    "Authorization": f"Bearer {SERVICE_KEY}",
    "Content-Type": "application/json"
}

headers_anon = {
    "apikey": ANON_KEY,
    "Content-Type": "application/json"
}

print("=== STEP 1: Check what users actually exist in Supabase Auth ===")
res1 = requests.get(f"{SUPABASE_URL}/auth/v1/admin/users", headers=headers_admin)
if res1.status_code == 200:
    users = res1.json().get("users", [])
    print(f"Total users in Supabase Auth: {len(users)}")
    for u in users:
        print(f"  email: {u.get('email')} | confirmed: {u.get('email_confirmed_at') is not None} | id: {u.get('id')}")
else:
    print(f"Failed to list users: {res1.status_code} - {res1.text[:100]}")

print("\n=== STEP 2: Reset passwords for all seeded users ===")
password_map = {
    "aarav@placement360.dev": "Student@123",
    "priya.p@placement360.dev": "Student@123",
    "rahul@placement360.dev": "Student@123",
    "sneha@placement360.dev": "Student@123",
    "arjun@placement360.dev": "Student@123",
    "drpriya@placement360.dev": "Faculty@123",
    "ravi@placement360.dev": "Faculty@123",
}

if res1.status_code == 200:
    users = res1.json().get("users", [])
    for user in users:
        email = user.get("email")
        user_id = user.get("id")
        password = password_map.get(email)
        
        if not password:
            continue
        
        # Update password via admin API
        res2 = requests.put(
            f"{SUPABASE_URL}/auth/v1/admin/users/{user_id}",
            headers=headers_admin,
            json={
                "password": password,
                "email_confirm": True
            }
        )
        
        if res2.status_code == 200:
            print(f"PASS: Password reset: {email}")
        else:
            print(f"FAIL: {email}: {res2.status_code} - {res2.text[:100]}")

print("\n=== STEP 3: Test login directly after password reset ===")
test_cases = [
    ("priya.p@placement360.dev", "Student@123"),
    ("drpriya@placement360.dev", "Faculty@123"),
]

for email, password in test_cases:
    res3 = requests.post(
        f"{SUPABASE_URL}/auth/v1/token?grant_type=password",
        headers=headers_anon,
        json={"email": email, "password": password}
    )
    print(f"{email}: {res3.status_code}")
    if res3.status_code == 200:
        print(f"  PASS: Login works - user_id: {res3.json()['user']['id']}")
    else:
        print(f"  FAIL: Error: {res3.text[:150]}")

print("\n=== STEP 4: Test the full backend login endpoint ===")
# Note: Ensure backend is running on 8000
try:
    res4 = requests.post(f"{BASE}/auth/login", json={
        "email": "priya.p@placement360.dev",
        "password": "Student@123"
    })
    print(f"Backend login: {res4.status_code}")
    if res4.status_code == 200:
        print(res4.json())
    else:
        print(f"Error: {res4.text[:200]}")
except Exception as e:
    print(f"Backend request failed: {str(e)}")
