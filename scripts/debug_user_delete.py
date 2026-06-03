import os, requests
from dotenv import load_dotenv
load_dotenv(dotenv_path=r"c:\Users\PRIHTVIRAJ\Desktop\P360_BACKEND\placement360-backend\.env")

SUPABASE_URL = os.getenv("SUPABASE_URL")
SERVICE_KEY = os.getenv("SUPABASE_SERVICE_ROLE_KEY")

headers = {
    "apikey": SERVICE_KEY,
    "Authorization": f"Bearer {SERVICE_KEY}"
}

ids = ["00000000-0000-0000-0000-000000000001", "00000000-0000-0000-0000-000000000002"]
for id in ids:
    res = requests.delete(f"{SUPABASE_URL}/auth/v1/admin/users/{id}", headers=headers)
    print(f"Delete {id}: {res.status_code}")
