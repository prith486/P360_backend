"""
API dependencies for authentication and permission handling.
Using local JWT verification (no Supabase Auth calls for token validation).
"""
import uuid
import logging
from datetime import datetime, timezone
from typing import Optional

from fastapi import Depends, HTTPException, status, Security
from fastapi.security import OAuth2PasswordBearer, HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.orm import Session
from jose import jwt, JWTError
from supabase import create_client, Client

from app.core.config import settings
from app.core.database import get_db
from app.models.auth_user import AuthUser
from app.models.student import Student
from app.models.faculty import Faculty
from app.models.enums import UserRole, BranchType, AcademicYear

# Logging setup
logger = logging.getLogger(__name__)

# Re-using OAuth scheme for Swagger UI integration
oauth2_scheme = OAuth2PasswordBearer(
    tokenUrl=f"{settings.API_V1_STR}/auth/login"
)

security = HTTPBearer(auto_error=False)

def decode_token(credentials: Optional[HTTPAuthorizationCredentials]) -> dict:
    """Helper to decode JWT or legacy mock token. Raises 401 on failure."""
    if not credentials:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Not authenticated",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    token = credentials.credentials
    
    # Support both real JWTs and mock token strings
    if token.startswith("mock_valid_"):
        parts = token.split("_")
        if len(parts) >= 4:
            user_id = parts[-1]
            role = parts[2]
            return {"sub": user_id, "role": role, "email": f"test@{role}.com", "name": f"Test {role.capitalize()}", "mock": True}
        else:
            raise HTTPException(status_code=401, detail="Malformed mock token")
    
    try:
        payload = jwt.decode(
            token,
            settings.SECRET_KEY,
            algorithms=[settings.ALGORITHM]
        )
        return payload
    except JWTError as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=f"Invalid token: {str(e)}",
            headers={"WWW-Authenticate": "Bearer"},
        )

# -----------------------------------------------------------------------------
# Supabase Client (Legacy fallback for non-auth operations if needed)
# -----------------------------------------------------------------------------
_supabase_client: Optional[Client] = None

def get_supabase_client() -> Client:
    """Get or create Supabase client instance."""
    global _supabase_client
    if _supabase_client is None:
        _supabase_client = create_client(
            settings.SUPABASE_URL if hasattr(settings, "SUPABASE_URL") else "", 
            settings.SUPABASE_KEY if hasattr(settings, "SUPABASE_KEY") else ""
        )
    return _supabase_client

# -----------------------------------------------------------------------------
# Local JWT Verification
# -----------------------------------------------------------------------------
def _verify_token(token: str) -> dict:
    """Verify the JWT signature locally using the app's SECRET_KEY."""
    try:
        payload = jwt.decode(
            token,
            settings.SECRET_KEY,
            algorithms=[settings.ALGORITHM]
        )
        return payload
    except JWTError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )

async def get_current_user_id(
    credentials: HTTPAuthorizationCredentials = Security(security)
) -> uuid.UUID:
    """Return the user's UUID from the bearer token using local verification."""
    payload = _verify_token(credentials.credentials)
    sub = payload.get("sub")
    if not sub:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token: missing subject",
            headers={"WWW-Authenticate": "Bearer"},
        )
    return uuid.UUID(sub)

# -----------------------------------------------------------------------------
# Dependency: get_current_user
# -----------------------------------------------------------------------------
def get_current_user(
    user_id: uuid.UUID = Depends(get_current_user_id),
    db: Session = Depends(get_db)
) -> AuthUser:
    """
    Get current user details from DB based on local JWT sub claim.
    """
    user = db.query(AuthUser).filter(AuthUser.id == user_id).first()
    if user:
        return user

    # Fallback to hardcoded mock for deterministic demo IDs if not in DB
    mock_ids = [
        uuid.UUID("00000000-0000-0000-0000-000000000001"),
        uuid.UUID("00000000-0000-0000-0000-000000000002")
    ]
    if user_id in mock_ids:
        is_student = user_id == mock_ids[0]
        role = "student" if is_student else "faculty"
        name = "Aarav Sharma" if is_student else "Dr. Priya Sharma"
        email = f"{'aarav' if is_student else 'priya'}@placement360.dev"
        
        return AuthUser(
            id=user_id,
            email=email,
            full_name=name,
            raw_app_meta_data={"role": role},
            email_confirmed_at=datetime.now(timezone.utc)
        )

    raise HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="User not found in system",
        headers={"WWW-Authenticate": "Bearer"},
    )

async def get_current_active_user(
    credentials: Optional[HTTPAuthorizationCredentials] = Security(security),
):
    """Generic auth — works for both faculty and student tokens."""
    payload = decode_token(credentials)
    
    user_id = payload.get("sub")
    role = payload.get("role")
    
    if not user_id:
        raise HTTPException(status_code=401, detail="No user_id in token")
    
    if not role:
        raise HTTPException(status_code=401, detail="No role in token")
    
    # Return a simple dict with user info — endpoints that need this
    # just need to know who is calling, not the full profile
    return {
        "user_id": user_id,
        "role": role,
        "email": payload.get("email"),
        "name": payload.get("name"),
        "mock": payload.get("mock", False)
    }

# -----------------------------------------------------------------------------
# Dependency: get_current_student
# -----------------------------------------------------------------------------
async def get_current_student(
    credentials: Optional[HTTPAuthorizationCredentials] = Security(security),
    db: Session = Depends(get_db)
) -> Student:
    """Get current student by verifying token locally and checking role."""
    payload = decode_token(credentials)
    
    role = payload.get("role")
    if role != "student":
        raise HTTPException(status_code=403, detail=f"Not authorized — got role: {role}")
    
    user_id = payload.get("sub")
    if not user_id:
        raise HTTPException(status_code=401, detail="No user_id in token")
    
    student = db.query(Student).filter(Student.user_id == user_id).first()
    
    if not student:
        # Emergency fallback for demo mock student
        if str(user_id) == "00000000-0000-0000-0000-000000000001":
            mock_user = AuthUser(
                id=uuid.UUID(user_id),
                email="aarav@placement360.dev",
                full_name="Aarav Sharma",
                raw_app_meta_data={"role": "student"},
                email_confirmed_at=datetime.now(timezone.utc)
            )
            s = Student(
                user_id=uuid.UUID(user_id),
                roll_number="MOCK001",
                branch=BranchType.COMPUTER_SCIENCE,
                batch_year=2022,
                current_year=AcademicYear.FOURTH
            )
            s.user = mock_user
            return s
        raise HTTPException(status_code=404, detail=f"Student profile not found for user_id: {user_id}")
    return student

# -----------------------------------------------------------------------------
# Dependency: get_current_faculty
# -----------------------------------------------------------------------------
async def get_current_faculty(
    credentials: Optional[HTTPAuthorizationCredentials] = Security(security),
    db: Session = Depends(get_db)
) -> Faculty:
    """Get current faculty by verifying token locally and checking role."""
    payload = decode_token(credentials)
    
    role = payload.get("role")
    if role != "faculty":
        raise HTTPException(status_code=403, detail=f"Not authorized — got role: {role}")
    
    user_id = payload.get("sub")
    if not user_id:
        raise HTTPException(status_code=401, detail="No user_id in token")
    
    faculty = db.query(Faculty).filter(Faculty.user_id == user_id).first()
    
    if not faculty:
        # Emergency fallback for demo mock faculty
        if str(user_id) == "00000000-0000-0000-0000-000000000002":
            mock_user = AuthUser(
                id=uuid.UUID(user_id),
                email="priya@placement360.dev",
                full_name="Dr. Priya Sharma",
                raw_app_meta_data={"role": "faculty"},
                email_confirmed_at=datetime.now(timezone.utc)
            )
            f = Faculty(
                user_id=uuid.UUID(user_id),
                employee_id="EMP001",
                department="Computer Science",
                designation="Professor"
            )
            f.user = mock_user
            return f
        raise HTTPException(status_code=404, detail=f"Faculty profile not found for user_id: {user_id}")
    return faculty

# -----------------------------------------------------------------------------
# Dependency: get_current_admin
# -----------------------------------------------------------------------------
def get_current_admin(
    current_user: dict = Depends(get_current_active_user),
):
    """Verify user is admin."""
    # 1. Mock admin support
    if str(current_user["user_id"]) == "00000000-0000-0000-0000-000000000002":
        return current_user
 
    # 2. Real admin check (if applicable)
    role = current_user.get("role")
    if role in ["admin", "service_role", "faculty"]:
        # In current mock setup, faculty is our admin equivalent
        return current_user
 
    raise HTTPException(
        status_code=status.HTTP_403_FORBIDDEN,
        detail="The user doesn't have enough privileges"
    )
