"""
Script to generate valid JWT tokens for existing users.
Useful for testing endpoints via Swagger UI or curl.

Usage:
    python scripts/generate_token.py <email>
    python scripts/generate_token.py --list
"""

import sys
from pathlib import Path
from sqlalchemy import text

# Add project root to Python path
sys.path.insert(0, str(Path(__file__).parent.parent))

from app.core.database import SessionLocal
from app.core.security import create_access_token

def generate_token_for_email(email: str) -> None:
    """Generate JWT token for user with given email."""
    db = SessionLocal()
    try:
        # Find user by email using raw SQL to avoid ORM relationship issues during testing
        query = text("SELECT id, email, role, status, full_name FROM users WHERE email = :email")
        result = db.execute(query, {"email": email}).mappings().fetchone()
        
        if not result:
            print(f"Error: User with email '{email}' not found.")
            print("\nAvailable users:")
            list_users()
            return
        
        # Generate token
        token = create_access_token(subject=result.id)
        
        print(f"\n{'='*60}")
        print(f"Token for: {result.full_name}")
        print(f"Email: {result.email}")
        print(f"Role: {result.role}")
        print(f"Status: {result.status}")
        print(f"{'='*60}")
        print(f"\nBearer Token:")
        print(f"Bearer {token}")
        print(f"\n{'='*60}")
        print(f"\nFor curl:")
        print(f'curl -H "Authorization: Bearer {token}" http://localhost:8000/api/v1/students/me')
        print(f"\nFor Swagger UI:")
        print(f"1. Click 'Authorize' button")
        print(f"2. Paste token (without 'Bearer ' prefix)")
        print(f"{'='*60}\n")
        
    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()
    finally:
        db.close()


def list_users() -> None:
    """List all users in database."""
    db = SessionLocal()
    try:
        # Use raw SQL to avoid ORM relationship loading issues
        query = text("SELECT id, email, full_name, role FROM users LIMIT 20")
        users = db.execute(query).mappings().all()
        
        if not users:
            print("No users found in database.")
            return
            
        print(f"\n{'='*60}")
        print("Available Users:")
        print(f"{'='*60}")
        for u in users:
            print(f"  {u.id}: {u.email} - {u.full_name} ({u.role})")
        print(f"{'='*60}\n")
    except Exception as e:
        print(f"Error listing users: {e}")
        # If table doesn't exist, this might fail, which is expected if not initialized
    finally:
        db.close()


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python scripts/generate_token.py <email>")
        print("       python scripts/generate_token.py --list")
        print("\nExamples:")
        print("  python scripts/generate_token.py student1@placement360.com")
        print("  python scripts/generate_token.py admin@placement360.com")
        print("  python scripts/generate_token.py --list")
        sys.exit(1)
    
    if sys.argv[1] == "--list":
        list_users()
    else:
        generate_token_for_email(sys.argv[1])
