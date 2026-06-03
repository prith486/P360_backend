"""
Mock Authentication Endpoints — DEVELOPMENT ONLY.

Only active when ENABLE_MOCK_AUTH=true in environment.
Returns 404 in production to prevent accidental exposure.

Usage:
  POST /api/v1/auth/mock-login  { "role": "student" | "faculty" }
  GET  /api/v1/auth/mock-me     (Authorization: Bearer <jwt>)
"""
from datetime import datetime, timedelta, timezone
from typing import Literal

from fastapi import APIRouter, HTTPException, status, Request
from jose import jwt, JWTError
from pydantic import BaseModel

from app.core.config import settings
from app.api.v1.auth import _create_local_jwt

router = APIRouter()

# ---------------------------------------------------------
# Constants — fixed UUIDs so mock data is deterministic
# ---------------------------------------------------------
MOCK_USERS = {
    "student": {
        "user_id": "00000000-0000-0000-0000-000000000001",
        "email": "aarav@placement360.dev",
        "role": "student",
        "name": "Aarav Sharma",
    },
    "faculty": {
        "user_id": "00000000-0000-0000-0000-000000000002",
        "email": "priya@placement360.dev",
        "role": "faculty",
        "name": "Dr. Priya Sharma",
    },
}


def _require_mock_auth_enabled() -> None:
    """Raise 404 if mock auth is disabled (production guard)."""
    if not settings.ENABLE_MOCK_AUTH:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Not found",  # deliberate vague message
        )


def _create_mock_jwt(user: dict) -> str:
    """
    Use shared helper to create a signed JWT.
    """
    return _create_local_jwt({
        "sub": user["user_id"],
        "role": user["role"],
        "email": user["email"],
        "name": user["name"],
        "mock": True
    })


# ---------------------------------------------------------
# Request / Response models
# ---------------------------------------------------------
class MockLoginRequest(BaseModel):
    role: Literal["student", "faculty"] = "student"


# ---------------------------------------------------------
# POST /api/v1/auth/mock-login
# ---------------------------------------------------------
@router.post("/mock-login", status_code=status.HTTP_200_OK)
async def mock_login(body: MockLoginRequest):
    """
    Skip Supabase entirely.  Generates a real JWT (signed with SECRET_KEY)
    that works with all protected endpoints.
    
    Structure matches Frontend-Backend API Contract.
    """
    _require_mock_auth_enabled()

    user = MOCK_USERS[body.role]
    token = _create_mock_jwt(user)

    # Split name into first/last for the user object
    name_parts = user["name"].split()
    first_name = name_parts[0] if name_parts else "Test"
    last_name = name_parts[-1] if len(name_parts) > 1 else body.role.capitalize()

    res_user = {
        "id": user["user_id"],
        "email": user["email"],
        "firstName": first_name,
        "lastName": last_name,
        "role": user["role"]
    }

    print(f"DEBUG MOCK LOGIN: successful for {body.role}, id={user['user_id']}")
    return {
        "success": True,
        "message": "Mock login successful",
        "access_token": token,  # Top-level for older/specific frontend versions
        "accessToken": token,   # Top-level camelCase
        "token": token,         # Extra compatibility
        "user": res_user,       # Top-level user object
        "role": user["role"],
        "user_id": user["user_id"],
        "data": {
            "user": res_user,
            "accessToken": token,
            "access_token": token,
            "refreshToken": f"mock_refresh_{user['user_id']}",
            "token_type": "bearer"
        }
    }


# ---------------------------------------------------------
# GET /api/v1/auth/mock-me
# ---------------------------------------------------------
@router.get("/mock-me")
async def mock_me(request: Request):
    """
    Decode the JWT from the Authorization header and return the
    user payload — no database query needed.

    Only available when ENABLE_MOCK_AUTH=true.
    Returns 404 otherwise.
    """
    _require_mock_auth_enabled()

    # Extract Bearer token
    auth_header = request.headers.get("Authorization", "")
    if not auth_header.startswith("Bearer "):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Authorization header missing or malformed",
            headers={"WWW-Authenticate": "Bearer"},
        )
    token = auth_header[len("Bearer "):]

    # Decode the JWT
    try:
        payload = jwt.decode(
            token,
            settings.SECRET_KEY,
            algorithms=[settings.ALGORITHM],
        )
    except JWTError as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=f"Invalid token: {e}",
            headers={"WWW-Authenticate": "Bearer"},
        )

    role = payload.get("role", "student")
    user_id = payload.get("sub", "")
    email = payload.get("email", "")

    name_parts = email.split("@")[0].split(".")
    first = name_parts[0].capitalize() if name_parts else "Test"
    last = name_parts[1].capitalize() if len(name_parts) > 1 else (
        "Student" if role == "student" else "Faculty"
    )

    return {
        "success": True,
        "data": {
            "id": user_id,
            "email": email,
            "firstName": first,
            "lastName": last,
            "role": role,
            "isVerified": True,
        },
    }
