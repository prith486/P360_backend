# This script creates Supabase Auth users for existing seeded DB rows
# Run once: python scripts/seed_auth_users.py

import os, requests
from dotenv import load_dotenv

# Use absolute path to .env
env_path = r"c:\Users\PRIHTVIRAJ\Desktop\P360_BACKEND\placement360-backend\.env"
load_dotenv(dotenv_path=env_path)

SUPABASE_URL = os.getenv("SUPABASE_URL")
SERVICE_KEY = os.getenv("SUPABASE_SERVICE_ROLE_KEY")

headers = {
    "apikey": SERVICE_KEY,
    "Authorization": f"Bearer {SERVICE_KEY}",
    "Content-Type": "application/json"
}

users_to_create = [
    {
        "id": "00000000-0000-0000-0000-000000000001",
        "email": "aarav@placement360.dev",
        "password": "Student@123",
        "email_confirm": True,
        "user_metadata": {"full_name": "Aarav Sharma", "role": "student"}
    },
    {
        "id": "00000000-0000-0000-0000-000000000002", 
        "email": "priya@placement360.dev",
        "password": "Faculty@123",
        "email_confirm": True,
        "user_metadata": {"full_name": "Dr. Priya Sharma", "role": "faculty"}
    }
]

for user in users_to_create:
    res = requests.post(
        f"{SUPABASE_URL}/auth/v1/admin/users",
        headers=headers,
        json=user
    )
    
    if res.status_code in [200, 201]:
        print(f"Created: {user['email']}")
    elif res.status_code == 422:
        print(f"Already exists (422): {user['email']}")
    elif res.status_code == 500 and "23505" in res.text:
         print(f"Already exists (23505): {user['email']}")
    else:
        print(f"Failed {user['email']}: {res.status_code} - {res.text[:100]}")
