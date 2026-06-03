import sys
import os
from pathlib import Path

# Add project root to Python path
sys.path.insert(0, str(Path(__file__).parent.parent))

from app.core.config import settings
from supabase import create_client

def verify():
    print(f"Verifying config...")
    print(f"SUPABASE_URL: {settings.SUPABASE_URL}")
    print(f"SUPABASE_KEY present: {bool(settings.SUPABASE_KEY)}")
    
    try:
        supabase = create_client(settings.SUPABASE_URL, settings.SUPABASE_KEY)
        print("Supabase client created successfully.")
        
        if settings.SUPABASE_SERVICE_ROLE_KEY:
            print("Testing Service Role Access...")
            admin_client = create_client(settings.SUPABASE_URL, settings.SUPABASE_SERVICE_ROLE_KEY)
            # Try to get users list to verify admin access
            # Note: The underlying library call might vary, usually list_users
            response = admin_client.auth.admin.list_users(page=1, per_page=1)
            print("✓ Successfully connected to Supabase Auth Admin API.")
            print(f"  Found {len(response)} users in page 1.")
        else:
            print("Service role key missing, skipping admin verification.")
            
    except Exception as e:
        print(f"✗ Verification failed: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    verify()
