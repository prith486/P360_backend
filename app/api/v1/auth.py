from fastapi import APIRouter, HTTPException, Depends, status, Body, Header
from sqlalchemy.orm import Session
import requests
from jose import jwt
from datetime import datetime, timedelta

from app.api.deps import get_supabase_client, get_current_user
from app.core.database import get_db
from app.core.config import settings
from app.schemas.auth import LoginRequest, RegisterRequest
from app.schemas.token import Token

# Models
from app.models.student import Student
from app.models.faculty import Faculty

router = APIRouter()

def _create_local_jwt(payload: dict) -> str:
    expire = datetime.utcnow() + timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    payload.update({"iat": datetime.utcnow(), "exp": expire, "type": "access"})
    return jwt.encode(payload, settings.SECRET_KEY, algorithm="HS256")

@router.post("/login")
async def login(
    email: str = Body(...),
    password: str = Body(...),
    db: Session = Depends(get_db)
):
    """Real login via Supabase Auth"""
    
    SUPABASE_URL = settings.SUPABASE_URL
    ANON_KEY = settings.SUPABASE_KEY # config.py calls it SUPABASE_KEY
    
    # Step 1 — authenticate with Supabase
    res = requests.post(
        f"{SUPABASE_URL}/auth/v1/token?grant_type=password",
        headers={
            "apikey": ANON_KEY,
            "Content-Type": "application/json"
        },
        json={"email": email, "password": password}
    )
    
    if res.status_code != 200:
        raise HTTPException(
            status_code=401,
            detail="Invalid email or password"
        )
    
    supabase_data = res.json()
    supabase_access_token = supabase_data["access_token"]
    supabase_refresh_token = supabase_data["refresh_token"]
    user_id = supabase_data["user"]["id"]
    
    # Step 2 — get role from user metadata
    role = supabase_data["user"].get("user_metadata", {}).get("role")
    if not role:
        role = supabase_data["user"].get("app_metadata", {}).get("role")
    
    if not role:
        raise HTTPException(status_code=400, detail="User role not configured")
    
    # Step 3 — fetch profile from DB
    if role == "student":
        profile = db.query(Student).filter(Student.user_id == user_id).first()
        if not profile:
            raise HTTPException(status_code=404, detail="Student profile not found")
        name = supabase_data["user"].get("user_metadata", {}).get("full_name", email)
    elif role == "faculty":
        profile = db.query(Faculty).filter(Faculty.user_id == user_id).first()
        if not profile:
            raise HTTPException(status_code=404, detail="Faculty profile not found")
        name = supabase_data["user"].get("user_metadata", {}).get("full_name", email)
    else:
        raise HTTPException(status_code=400, detail="Invalid role")
    
    # Step 4 — create local JWT (same as mock-login, so all endpoints work)
    local_token = _create_local_jwt({
        "sub": str(user_id),
        "role": role,
        "email": email,
        "name": name
    })
    
    return {
        "access_token": local_token,
        "refresh_token": supabase_refresh_token,
        "token_type": "bearer",
        "role": role,
        "user_id": str(user_id),
        "name": name,
        "email": email
    }

@router.post("/register/student")
async def register_student(
    email: str = Body(...),
    password: str = Body(...),
    full_name: str = Body(...),
    roll_number: str = Body(...),
    branch: str = Body(...),
    batch_year: int = Body(...),
    current_year: str = Body(...),
    db: Session = Depends(get_db)
):
    """Register a new student"""
    
    # Step 1 — validate college email format
    if not email.endswith((".edu", ".ac.in", "college.edu", "placement360.dev")):
        raise HTTPException(
            status_code=400,
            detail="Please use your college email address"
        )
    
    # Step 2 — check roll number not already registered
    existing = db.query(Student).filter(Student.roll_number == roll_number).first()
    if existing:
        raise HTTPException(status_code=409, detail="Roll number already registered")
    
    # Step 3 — create Supabase Auth user
    SERVICE_KEY = settings.SUPABASE_SERVICE_ROLE_KEY
    SUPABASE_URL = settings.SUPABASE_URL
    
    res = requests.post(
        f"{SUPABASE_URL}/auth/v1/admin/users",
        headers={
            "apikey": SERVICE_KEY,
            "Authorization": f"Bearer {SERVICE_KEY}",
            "Content-Type": "application/json"
        },
        json={
            "email": email,
            "password": password,
            "email_confirm": True,
            "user_metadata": {"full_name": full_name, "role": "student"}
        }
    )
    
    if res.status_code == 422:
        raise HTTPException(status_code=409, detail="Email already registered")
    
    if res.status_code not in [200, 201]:
        raise HTTPException(status_code=500, detail="Failed to create auth user")
    
    new_user_id = res.json()["id"]
    
    # Step 4 — create student profile in DB
    try:
        student = Student(
            user_id=new_user_id,
            roll_number=roll_number,
            branch=branch,
            batch_year=batch_year,
            current_year=current_year,
            readiness_score=0.0,
            profile_completion_percent=10.0
        )
        db.add(student)
        db.commit()
        db.refresh(student)
    except Exception as e:
        # Rollback: delete the auth user if DB insert fails
        requests.delete(
            f"{SUPABASE_URL}/auth/v1/admin/users/{new_user_id}",
            headers={
                "apikey": SERVICE_KEY,
                "Authorization": f"Bearer {SERVICE_KEY}"
            }
        )
        raise HTTPException(status_code=500, detail=f"Failed to create student profile: {str(e)}")
    
    # Step 5 — issue local JWT
    local_token = _create_local_jwt({
        "sub": str(new_user_id),
        "role": "student",
        "email": email,
        "name": full_name
    })
    
    return {
        "access_token": local_token,
        "token_type": "bearer",
        "role": "student",
        "user_id": str(new_user_id),
        "name": full_name,
        "email": email,
        "message": "Registration successful"
    }

@router.post("/register/faculty")
async def register_faculty(
    email: str = Body(...),
    password: str = Body(...),
    full_name: str = Body(...),
    employee_id: str = Body(...),
    department: str = Body(...),
    designation: str = Body(...),
    x_admin_secret: str = Header(..., alias="X-Admin-Secret"),
    db: Session = Depends(get_db)
):
    """Register a new faculty (Admin only)"""
    
    # Validation
    if x_admin_secret != settings.ADMIN_SECRET:
        raise HTTPException(status_code=403, detail="Invalid admin secret")
        
    # Check if employee_id already exists
    existing = db.query(Faculty).filter(Faculty.employee_id == employee_id).first()
    if existing:
        raise HTTPException(status_code=409, detail="Employee ID already registered")
        
    # Create Supabase Auth user
    SERVICE_KEY = settings.SUPABASE_SERVICE_ROLE_KEY
    SUPABASE_URL = settings.SUPABASE_URL
    
    res = requests.post(
        f"{SUPABASE_URL}/auth/v1/admin/users",
        headers={
            "apikey": SERVICE_KEY,
            "Authorization": f"Bearer {SERVICE_KEY}",
            "Content-Type": "application/json"
        },
        json={
            "email": email,
            "password": password,
            "email_confirm": True,
            "user_metadata": {"full_name": full_name, "role": "faculty"}
        }
    )
    
    if res.status_code == 422:
        raise HTTPException(status_code=409, detail="Email already registered")
        
    if res.status_code not in [200, 201]:
        raise HTTPException(status_code=500, detail="Failed to create auth user")
        
    new_user_id = res.json()["id"]
    
    # Create Faculty profile in DB
    try:
        faculty = Faculty(
            user_id=new_user_id,
            employee_id=employee_id,
            department=department,
            designation=designation
        )
        db.add(faculty)
        db.commit()
        db.refresh(faculty)
    except Exception as e:
        # Rollback
        requests.delete(
            f"{SUPABASE_URL}/auth/v1/admin/users/{new_user_id}",
            headers={
                "apikey": SERVICE_KEY,
                "Authorization": f"Bearer {SERVICE_KEY}"
            }
        )
        raise HTTPException(status_code=500, detail=f"Failed to create faculty profile: {str(e)}")
        
    # Issue local JWT
    local_token = _create_local_jwt({
        "sub": str(new_user_id),
        "role": "faculty",
        "email": email,
        "name": full_name
    })
    
    return {
        "access_token": local_token,
        "token_type": "bearer",
        "role": "faculty",
        "user_id": str(new_user_id),
        "name": full_name,
        "email": email,
        "message": "Faculty registration successful"
    }

@router.post("/refresh")
async def refresh_token(
    refresh_token: str = Body(..., embed=True),
    db: Session = Depends(get_db)
):
    """Refresh access token using Supabase refresh token"""
    
    res = requests.post(
        f"{settings.SUPABASE_URL}/auth/v1/token?grant_type=refresh_token",
        headers={
            "apikey": settings.SUPABASE_KEY,
            "Content-Type": "application/json"
        },
        json={"refresh_token": refresh_token}
    )
    
    if res.status_code != 200:
        raise HTTPException(status_code=401, detail="Invalid or expired refresh token")
    
    data = res.json()
    user_id = data["user"]["id"]
    role = data["user"].get("user_metadata", {}).get("role")
    if not role:
        role = data["user"].get("app_metadata", {}).get("role", "student")
        
    email = data["user"]["email"]
    name = data["user"].get("user_metadata", {}).get("full_name", email)
    
    # Issue new local JWT
    local_token = _create_local_jwt({
        "sub": str(user_id),
        "role": role,
        "email": email,
        "name": name
    })
    
    return {
        "access_token": local_token,
        "refresh_token": data["refresh_token"],
        "token_type": "bearer"
    }

@router.post("/forgot-password")
async def forgot_password(email: str = Body(...)):
    """Send password reset email via Supabase"""
    
    res = requests.post(
        f"{settings.SUPABASE_URL}/auth/v1/recover",
        headers={
            "apikey": settings.SUPABASE_KEY,
            "Content-Type": "application/json"
        },
        json={"email": email}
    )
    
    # Always return success to prevent email enumeration
    return {"message": "If this email is registered, a reset link has been sent"}




@router.post("/logout")
async def logout():
    """
    Logout user (invalidate session).
    Client should discard token.
    """
    return {"message": "Logged out successfully"}


@router.get("/me")
async def get_current_user_info(
    current_user = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Get current authenticated user's information.
    Returns user profile with role and verification status.
    """
    # Determine role from metadata
    role = "student"  # Default
    if current_user.raw_app_meta_data:
        role = current_user.raw_app_meta_data.get("role", "student")
    
    # Split full name into first and last
    name_parts = []
    if current_user.full_name:
        name_parts = current_user.full_name.split()
    
    first_name = name_parts[0] if len(name_parts) > 0 else ""
    last_name = name_parts[-1] if len(name_parts) > 1 else ""
    
    return {
        "success": True,
        "data": {
            "id": str(current_user.id),
            "email": current_user.email,
            "firstName": first_name,
            "lastName": last_name,
            "role": role,
            "isVerified": current_user.email_confirmed_at is not None
        }
    }
