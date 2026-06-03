import os, requests
from dotenv import load_dotenv
load_dotenv(dotenv_path=r"c:\Users\PRIHTVIRAJ\Desktop\P360_BACKEND\placement360-backend\.env")

SUPABASE_URL = os.getenv("SUPABASE_URL")
SERVICE_KEY = os.getenv("SUPABASE_SERVICE_ROLE_KEY")

headers = {
    "apikey": SERVICE_KEY,
    "Authorization": f"Bearer {SERVICE_KEY}",
}

res = requests.get(f"{SUPABASE_URL}/auth/v1/admin/users?per_page=100", headers=headers)
print(f"Status: {res.status_code}")
users = res.json().get('users', [])
print(f"Total: {len(users)}")
print(f"Emails: {[u['email'] for u in users]}")
