import sys
import socket
from pathlib import Path
from urllib.parse import urlparse

# Add project root to Python path
sys.path.insert(0, str(Path(__file__).parent.parent))

# Import settings to get the URL
from app.core.config import settings

def test_socket(host, port):
    print(f"Testing TCP connection to {host}:{port}...")
    try:
        # Resolve IP first to see what we're connecting to
        ip = socket.gethostbyname(host)
        print(f"  Resolved {host} to {ip}")
        
        sock = socket.create_connection((host, port), timeout=10)
        sock.close()
        print("✓ TCP connection successful!")
        return True
    except socket.timeout:
        print("✗ TCP connection failed: Timeout (Firewall or Network issue?)")
        return False
    except socket.gaierror:
        print("✗ TCP connection failed: DNS Resolution failed")
        return False
    except Exception as e:
        print(f"✗ TCP connection failed: {e}")
        return False

def verify_db():
    print("--- Database Diagnostics ---")
    url = settings.DATABASE_URL
    if not url:
        print("DATABASE_URL is not set in settings.")
        return

    try:
        # Mask password for printing
        safe_url = url
        if ":" in url and "@" in url:
            # Simple masking logic
            pass
            
        parsed = urlparse(url)
        host = parsed.hostname
        port = parsed.port or 5432
        
        print(f"Target: {host}:{port}")
        
        # 1. Test Network Connectivity
        if test_socket(host, port):
            # 2. Test Application Connectivity
            print("\nAttempting SQLAlchemy connection...")
            from app.core.database import SessionLocal
            from sqlalchemy import text
            
            try:
                db = SessionLocal()
                # Try simple query
                print("  Executing SELECT 1...")
                result = db.execute(text("SELECT 1")).scalar()
                print(f"✓ Connected! Result: {result}")
                
                # Try Version query
                version = db.execute(text("SELECT version()")).scalar()
                print(f"  DB Version: {version}")
                
                # Check auth schema
                print("  Checking auth schema access...")
                users = db.execute(text("SELECT count(*) FROM auth.users")).scalar()
                print(f"✓ Auth schema accessible. User count: {users}")
                
                db.close()
            except Exception as e:
                print(f"✗ SQLAlchemy connection failed: {e}")
                if "ssl" in str(e).lower() or "hba" in str(e).lower():
                    print("\nSuggestion: Try adding '?sslmode=require' to DATABASE_URL")

        else:
            print("\nDiagnostic Result: Network Unreachable")
            print("1. Check if a firewall is blocking outgoing port 5432.")
            print("2. Check if your ISP blocks database ports.")
            print("3. Verify the hostname is correct.")

    except Exception as e:
        print(f"Error executing script: {e}")

if __name__ == "__main__":
    verify_db()
