import requests, os
from dotenv import load_dotenv

# Path to .env 
env_path = r"c:\Users\PRIHTVIRAJ\Desktop\P360_BACKEND\placement360-backend\.env"
load_dotenv(dotenv_path=env_path)

SUPABASE_URL = os.getenv("SUPABASE_URL")
SERVICE_KEY = os.getenv("SUPABASE_SERVICE_ROLE_KEY")
BASE = "http://localhost:8000/api/v1"

headers = {"apikey": SERVICE_KEY, "Authorization": f"Bearer {SERVICE_KEY}"}

print("--- Final Verification ---")

# 1. Check auth users count
try:
    res = requests.get(f"{SUPABASE_URL}/auth/v1/admin/users", headers=headers)
    if res.status_code == 200:
        users = res.json().get('users', [])
        print(f"Total auth users: {len(users)}")
    else:
        print(f"Failed to list users: {res.status_code}")
except Exception as e:
    print(f"Connection failed: {str(e)}")

# 2. Test real login (aarav)
try:
    res2 = requests.post(f"{BASE}/auth/login", json={
        "email": "aarav@placement360.dev",
        "password": "Student@123"
    })
    print(f"Real login (student): {res2.status_code}")
    if res2.status_code == 200:
        print(f"  name: {res2.json().get('name')}")
        print(f"  role: {res2.json().get('role')}")
    else:
        print(f"  error: {res2.text[:200]}")
except Exception as e:
    print(f"Real login request failed: {str(e)}")

# 3. Test real login (faculty)
try:
    res3 = requests.post(f"{BASE}/auth/login", json={
        "email": "ravi@placement360.dev", 
        "password": "Faculty@123"
    })
    print(f"Real login (faculty): {res3.status_code}")
    if res3.status_code == 200:
        print(f"  name: {res3.json().get('name')}")
        print(f"  role: {res3.json().get('role')}")
    else:
        print(f"  error: {res3.text[:200]}")
except Exception as e:
    print(f"Real faculty login request failed: {str(e)}")

# 4. Test mock login still works
try:
    res4 = requests.post(f"{BASE}/auth/mock-login", json={"role": "student"})
    print(f"Mock login still works: {res4.status_code}")
except Exception as e:
    print(f"Mock login request failed: {str(e)}")
