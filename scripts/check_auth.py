import os, requests
from dotenv import load_dotenv

# Path to .env 
env_path = r"c:\Users\PRIHTVIRAJ\Desktop\P360_BACKEND\placement360-backend\.env"
load_dotenv(dotenv_path=env_path)

SUPABASE_URL = os.getenv("SUPABASE_URL")
SERVICE_KEY = os.getenv("SUPABASE_SERVICE_ROLE_KEY")

if not SUPABASE_URL or not SERVICE_KEY:
    print(f"ERROR: SUPABASE_URL or SERVICE_KEY missing from environment.")
    print(f"SUPABASE_URL: {SUPABASE_URL}")
    print(f"SERVICE_KEY: {'[PROTECTED]' if SERVICE_KEY else None}")
else:
    headers = {
        "apikey": SERVICE_KEY,
        "Authorization": f"Bearer {SERVICE_KEY}",
        "Content-Type": "application/json"
    }

    # Try to list existing auth users
    res = requests.get(
        f"{SUPABASE_URL}/auth/v1/admin/users",
        headers=headers
    )
    print(f"List users status: {res.status_code}")
    if res.status_code == 200:
        users = res.json()
        print(f"Total auth users: {len(users.get('users', []))}")
        for u in users.get('users', [])[:3]:
            print(f"  - {u.get('email')} | role: {u.get('raw_app_meta_data', {}).get('role')}")
    else:
        print(f"Error: {res.text[:200]}")

    # Check seeded users
    res2 = requests.get(
        f"{SUPABASE_URL}/auth/v1/admin/users/00000000-0000-0000-0000-000000000001",
        headers=headers
    )
    print(f"\nSeeded student in auth: {res2.status_code}")

    res3 = requests.get(
        f"{SUPABASE_URL}/auth/v1/admin/users/00000000-0000-0000-0000-000000000002", 
        headers=headers
    )
    print(f"Seeded faculty in auth: {res3.status_code}")
