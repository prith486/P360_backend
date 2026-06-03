import os, requests
from dotenv import load_dotenv
load_dotenv()

SUPABASE_URL = os.getenv("SUPABASE_URL")
SERVICE_KEY = os.getenv("SUPABASE_SERVICE_ROLE_KEY")

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
    users_data = res.json()
    users = users_data.get('users', [])
    print(f"Total auth users: {len(users)}")
    for u in users[:3]:
        print(f"  - {u.get('email')} | role: {u.get('raw_app_meta_data', {}).get('role')}")
else:
    print(f"Error: {res.text[:200]}")

# 5. Check seeded users
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
