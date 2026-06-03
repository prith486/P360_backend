import os, requests
from dotenv import load_dotenv
load_dotenv(dotenv_path=r"c:\Users\PRIHTVIRAJ\Desktop\P360_BACKEND\placement360-backend\.env")

SUPABASE_URL = os.getenv("SUPABASE_URL")
SERVICE_KEY = os.getenv("SUPABASE_SERVICE_ROLE_KEY")

headers = {
    "apikey": SERVICE_KEY,
    "Authorization": f"Bearer {SERVICE_KEY}",
    "Content-Type": "application/json"
}

users = [
    {"email": "aarav@placement360.dev", "password": "Student@123"},
    {"email": "ravi@placement360.dev", "password": "Faculty@123"}
]

for user in users:
    # Get user by email to find ID
    res_list = requests.get(f"{SUPABASE_URL}/auth/v1/admin/users", headers=headers)
    user_id = None
    for u in res_list.json().get('users', []):
        if u['email'] == user['email']:
            user_id = u['id']
            break
            
    if user_id:
        # Update password
        res_upd = requests.put(
            f"{SUPABASE_URL}/auth/v1/admin/users/{user_id}",
            headers=headers,
            json={"password": user["password"]}
        )
        print(f"Updated {user['email']}: {res_upd.status_code}")
    else:
        print(f"Not found: {user['email']}")
