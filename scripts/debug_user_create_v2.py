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

user = {
    "id": "00000000-0000-0000-0000-000000000003",
    "email": "test2@placement360.dev",
    "password": "Password@123",
    "email_confirm": True,
    "user_metadata": {"full_name": "Test User 2", "role": "student"}
}

res = requests.post(f"{SUPABASE_URL}/auth/v1/admin/users", headers=headers, json=user)
print(f"Status: {res.status_code}")
print(f"Body: {res.text}")
