# Backend Server Startup Issue - Complete Context

## CRITICAL PROBLEM
The FastAPI backend server **cannot start** - it either hangs silently on startup or shows `ModuleNotFoundError: No module named 'app'`.

---

## Project Structure
```
c:\Users\PRIHTVIRAJ\Desktop\P360_BACKEND\placement360-backend\
├── .env (exists, configured)
├── app/
│   ├── __init__.py (✅ CREATED by me - keep this)
│   ├── main.py
│   ├── models/
│   │   └── auth_user.py (⚠️ MODIFIED - added is_active property)
│   ├── schemas/
│   │   └── user.py (⚠️ MODIFIED MULTIPLE TIMES - this is the problem)
│   ├── api/
│   ├── core/
│   └── ...
├── venv/ (exists, all packages installed including uvicorn, fastapi, pydantic 2.12.5)
└── requirements.txt
```

---

## Original Problem We Were Trying to Fix

**Endpoint:** `GET /api/v1/faculty/me`  
**Status:** Returns 500 Internal Server Error

**Error Message:**
```python
fastapi.exceptions.ResponseValidationError: 2 validation errors:
  {
    'type': 'string_type', 
    'loc': ('response', 'user', 'role'), 
    'msg': 'Input should be a valid string', 
    'input': None
  }
  {
    'type': 'bool_type', 
    'loc': ('response', 'user', 'is_active'), 
    'msg': 'Input should be a valid boolean', 
    'input': <bound method AuthUser.is_active of <AuthUser>>
  }
```

**Root Cause:**
- `FacultyDetailed` schema includes `user: UserRead`
- When FastAPI tries to serialize `AuthUser` ORM object → `UserRead` Pydantic model:
  - `AuthUser.role` column is "authenticated" (or None), but app role is in `raw_app_meta_data.role` ("faculty")
  - `AuthUser` has `is_account_active` property, but UserRead looks for `is_active`
  - Pydantic sees `is_active` as a bound method reference, not a boolean

---

## Files Modified (Chronological Order)

### 1. ✅ `app/__init__.py` (CREATED)
**Status:** KEEP THIS FILE

```python
"""
Placement360 Backend Application Package
"""
```

**Why:** This file was missing. Python needs `__init__.py` to recognize `app` as a package.

---

### 2. ⚠️ `app/models/auth_user.py` (MODIFIED)
**Status:** KEEP THIS CHANGE

**Change:** Added `is_active` property at line ~116

```python
@property
def is_account_active(self) -> bool:
    """Boolean property for UserRead."""
    if self.deleted_at is not None:
        return False
    if self.banned_until is not None and self.banned_until > datetime.now(timezone.utc):
        return False
    return True

# ✅ ADDED THIS:
@property
def is_active(self) -> bool:
    """Alias for is_account_active for backward compatibility."""
    return self.is_account_active
```

**Why:** Pydantic's `from_attributes=True` looks for `is_active` on the ORM object. AuthUser only had `is_account_active`, so we added an alias property.

**Existing properties in AuthUser:**
- `computed_role` → returns role from `raw_app_meta_data.role` or falls back to "authenticated"
- `full_name` → extracts from `raw_user_meta_data`
- `is_account_active` → checks deleted_at and banned_until
- `is_active` → NEW alias for is_account_active

---

### 3. ❌ `app/schemas/user.py` (MODIFIED MULTIPLE TIMES - THIS IS THE PROBLEM)

**Current State (FINAL VERSION after multiple failed attempts):**

```python
"""
Pydantic schemas for User model.
"""

import uuid
from datetime import datetime
from typing import Optional, Any

from pydantic import BaseModel, EmailStr, Field, ConfigDict

from app.models.enums import UserRole, UserStatus


class UserBase(BaseModel):
    """Base schema with common fields."""
    email: EmailStr
    full_name: str = Field(..., min_length=2, max_length=255)
    phone_number: Optional[str] = Field(None, max_length=15)
    profile_picture_url: Optional[str] = Field(None, max_length=500)


class UserCreate(UserBase):
    """Schema for creating new user."""
    password: str = Field(..., min_length=8, max_length=128)
    role: UserRole = UserRole.STUDENT


class UserUpdate(BaseModel):
    """Schema for updating user profile."""
    full_name: Optional[str] = Field(None, min_length=2, max_length=255)
    phone_number: Optional[str] = Field(None, max_length=15)
    profile_picture_url: Optional[str] = Field(None, max_length=500)


class PasswordChange(BaseModel):
    """Schema for password change."""
    old_password: str = Field(..., min_length=8)
    new_password: str = Field(..., min_length=8, max_length=128)


class UserRead(BaseModel):
    """Schema for user response (AuthUser compatible)."""
    id: uuid.UUID
    email: str
    full_name: Optional[str] = ""
    role: str = "authenticated"
    is_active: bool = True
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    email_confirmed_at: Optional[datetime] = None

    model_config = ConfigDict(from_attributes=True)
    
    @classmethod
    def from_auth_user(cls, auth_user):
        """Create UserRead from AuthUser with proper field mapping."""
        return cls(
            id=auth_user.id,
            email=auth_user.email or "",
            full_name=auth_user.full_name or "",
            role=auth_user.computed_role if hasattr(auth_user, 'computed_role') else "authenticated",
            is_active=auth_user.is_active if hasattr(auth_user, 'is_active') else True,
            created_at=auth_user.created_at,
            updated_at=auth_user.updated_at,
            email_confirmed_at=auth_user.email_confirmed_at
        )


class UserInList(BaseModel):
    """Minimal schema for list views."""
    id: uuid.UUID
    email: EmailStr
    full_name: Optional[str] = None
    role: Optional[str] = None

    model_config = ConfigDict(from_attributes=True)
```

**Problem with Current Approach:**
- The `from_auth_user()` classmethod won't be called automatically by FastAPI
- When FastAPI serializes responses, it uses `UserRead.model_validate(auth_user_obj)`
- This bypasses our custom `from_auth_user()` method
- So the 500 error will still happen

---

## What I Tried (And Why Each Failed)

### ❌ Attempt 1: `@model_validator(mode='before')`
```python
@model_validator(mode='before')
@classmethod
def extract_from_orm(cls, values: Any) -> Any:
    if isinstance(values, dict):
        return values
    # Build dict from ORM object...
    result = {...}
    return result
```
**Result:** Server hung on startup (never printed ANY output)

---

### ❌ Attempt 2: `@field_validator` with `mode='before'`
```python
@field_validator('role', mode='before')
@classmethod
def validate_role(cls, v, info):
    if v is None:
        # Try to get from info.data...
        return "authenticated"
    return v

@field_validator('is_active', mode='before')
@classmethod
def validate_is_active(cls, v):
    if callable(v):
        return v()
    return bool(v)
```
**Result:** Server hung on startup

---

### ❌ Attempt 3: `Field(validation_alias=...)`
```python
role: str = Field(default="authenticated", validation_alias="computed_role")
is_active: bool = Field(default=True, validation_alias="is_account_active")
```
**Result:** Server hung on startup

---

### ❌ Attempt 4: `@model_validator(mode='wrap')`
```python
@model_validator(mode='wrap')
@classmethod
def extract_from_orm(cls, value: Any, handler, info):
    if isinstance(value, dict):
        return handler(value)
    data = {
        "id": getattr(value, 'id', None),
        "role": getattr(value, 'computed_role', None) or "authenticated",
        # ...
    }
    return handler(data)
```
**Result:** Server hung on import

---

### ❌ Attempt 5: `@model_serializer`
```python
@model_serializer(when_used='always')
def serialize_model(self) -> dict[str, Any]:
    return {...}
```
**Result:** Server hung

---

### ⚠️ Attempt 6: Custom `@classmethod from_auth_user()` (CURRENT)
**Result:** 
- ✅ Server doesn't hang anymore
- ❌ But this method won't be called automatically by FastAPI
- ❌ The 500 error will still occur because FastAPI uses `model_validate()` directly

---

## Current Startup Error

When trying to start the server from `C:\Users\PRIHTVIRAJ\Desktop\P360_BACKEND\placement360-backend\`:

```powershell
# Both of these fail:
.\venv\Scripts\uvicorn.exe app.main:app --host 0.0.0.0 --port 8000 --reload
.\venv\Scripts\python.exe -m uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload

# Error:
ModuleNotFoundError: No module named 'app'
```

**When I try to import manually:**
```powershell
.\venv\Scripts\python.exe -c "from app.main import app; print('Success')"
# Result: Hangs forever (no output)
```

---

## Possible Root Causes

1. **Circular Import:** Something in the import chain is circular
2. **Database Connection Blocking:** The `lifespan` function in `main.py` calls `test_connection()` which might hang
3. **Pydantic Validators at Import Time:** Some validator is executing during module import
4. **Missing `__init__.py` in subdirectories:** Maybe other subdirectories need `__init__.py` files?

---

## Environment Details

- **Python Version:** (from venv)
- **Pydantic Version:** 2.12.5
- **FastAPI Version:** 0.115.6
- **SQLAlchemy Version:** 2.0.36
- **Database:** Supabase PostgreSQL
- **.env file:** ✅ Exists and configured
- **All packages installed:** ✅ Confirmed via `pip list`

---

## Files That Need Investigation

1. **`app/main.py`** - Check the `lifespan` function and imports
2. **`app/core/database.py`** - Check `test_connection()` function
3. **`app/schemas/user.py`** - Need proper Pydantic v2 approach for ORM mapping
4. **`app/api/deps.py`** - How mock users are created
5. **All `__init__.py` files** - Make sure they exist in all subdirectories

---

## What Works (Before My Changes)

According to the user, these endpoints were working:
- ✅ `GET /api/v1/auth/me` → 200
- ✅ `GET /api/v1/students/me` → 200
- ✅ `GET /api/v1/students/dashboard` → 200
- ✅ `GET /api/v1/faculty/dashboard` → 200
- ❌ `GET /api/v1/faculty/me` → 500 (this is what we tried to fix)

---

## Questions for Backend Agent

1. **Why is the server hanging on import?** Is there a circular import or blocking database call?

2. **What's the CORRECT Pydantic v2 approach to map:**
   - `AuthUser.computed_role` (property) → `UserRead.role` (str)
   - `AuthUser.is_active` (property) → `UserRead.is_active` (bool)
   
   Without using validators that execute at import time?

3. **Should I:**
   - Use `model_serializer` instead of `model_validator`?
   - Modify the endpoints to manually call `UserRead.from_auth_user()`?
   - Use a different approach entirely?

4. **Is the issue in `app/main.py` lifespan function?** Should I comment out `test_connection()` to test?

---

## How to Test

```powershell
# Navigate to project
cd C:\Users\PRIHTVIRAJ\Desktop\P360_BACKEND\placement360-backend

# Try to import (currently hangs)
.\venv\Scripts\python.exe -c "from app.main import app; print('Success')"

# Try to start server (currently fails)
.\venv\Scripts\python.exe -m uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload

# Expected: Server starts and prints:
# INFO:     Uvicorn running on http://0.0.0.0:8000 (Press CTRL+C to quit)
# INFO:     Started reloader process
# INFO:     Started server process
# INFO:     Waiting for application startup.
# INFO:     Application startup complete.
```

---

## Next Steps Needed

1. **Fix the import hang** - Server must be able to start
2. **Fix the UserRead schema** - Properly map AuthUser properties without breaking startup
3. **Test GET /faculty/me** - Confirm it returns 200 instead of 500
4. **Complete Phase 1 fixes** - Add validators to student.py, fix route ordering

---

## Additional Files to Share (if needed)

Let me know if you need to see:
- `app/main.py` (startup/lifespan logic)
- `app/core/database.py` (database connection)
- `app/api/v1/faculty.py` (faculty endpoints)
- `app/schemas/faculty.py` (FacultyDetailed schema)
- Full error traceback (if we can get the server to output it)
