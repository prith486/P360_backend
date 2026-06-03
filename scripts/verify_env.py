import os
from dotenv import load_dotenv

# Use the absolute path to the .env file
env_path = r"c:\Users\PRIHTVIRAJ\Desktop\P360_BACKEND\placement360-backend\.env"
load_dotenv(dotenv_path=env_path)

vars_to_check = [
    "SUPABASE_URL",
    "SUPABASE_ANON_KEY", 
    "SUPABASE_SERVICE_ROLE_KEY",
    "SUPABASE_JWT_SECRET",
    "SECRET_KEY",
    "DATABASE_URL",
]

for var in vars_to_check:
    val = os.getenv(var)
    if val:
        print(f"{var}: EXISTS (length={len(val)})")
    else:
        print(f"{var}: MISSING")
