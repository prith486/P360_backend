**Context:**
Placement360 FastAPI backend. Supabase Auth is now properly configured with all 4 keys in `.env`. Email confirmation is disabled. `auth.users` is currently empty. We need to build real authentication alongside the existing mock-login which must keep working.

**Goal:** Build real email+password auth using Supabase Auth as the identity provider, while keeping local JWT verification for all protected endpoints (already working).

---

### Task 1 — Create Auth Users for Existing Seeded Data

The `public.students` and `public.faculty` tables have seeded rows but no corresponding `auth.users` entries. Create a script that fixes this.

Create `scripts/seed_auth_users.py`:

```python
# This script creates Supabase Auth users for existing seeded DB rows
# Run once: python scripts/seed_auth_users.py

import os, requests
from dotenv import load_dotenv
load_dotenv()

SUPABASE_URL = os.getenv("SUPABASE_URL")
SERVICE_KEY = os.getenv("SUPABASE_SERVICE_ROLE_KEY")

headers = {
    "apikey": SERVICE_KEY,
    "Authorization": f"Bearer {SERVICE_KEY}",
    "Content-Type": "application/json"
}

users_to_create = [
    {
        "id": "00000000-0000-0000-0000-000000000001",
        "email": "aarav@placement360.dev",
        "password": "Student@123",
        "email_confirm": True,
        "user_metadata": {"full_name": "Aarav Sharma", "role": "student"}
    },
    {
        "id": "00000000-0000-0000-0000-000000000002", 
        "email": "priya@placement360.dev",
        "password": "Faculty@123",
        "email_confirm": True,
        "user_metadata": {"full_name": "Dr. Priya Sharma", "role": "faculty"}
    }
]

for user in users_to_create:
    res = requests.post(
        f"{SUPABASE_URL}/auth/v1/admin/users",
        headers=headers,
        json=user
    )
    if res.status_code in [200, 201]:
        print(f"Created: {user['email']}")
    elif res.status_code == 422:
        print(f"Already exists: {user['email']}")
    else:
        print(f"Failed {user['email']}: {res.status_code} - {res.text[:100]}")
```

Run this script and paste the output confirming both users were created.

---

### Task 2 — Build Real Login Endpoint

Add `POST /api/v1/auth/login` that uses Supabase Auth:

In `app/api/v1/auth.py` (or wherever auth routes live), add:

```python
@router.post("/login")
async def login(
    email: str = Body(...),
    password: str = Body(...),
    db: Session = Depends(get_db)
):
    """Real login via Supabase Auth"""
    
    SUPABASE_URL = settings.SUPABASE_URL
    ANON_KEY = settings.SUPABASE_ANON_KEY
    
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
        name_parts = supabase_data["user"].get("user_metadata", {}).get("full_name", "").rsplit(" ", 1)
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
```

The key insight: Supabase validates the password, but we still issue our own local JWT so all existing protected endpoints keep working without change.

---

### Task 3 — Build Student Registration Endpoint

Add `POST /api/v1/auth/register/student`:

```python
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
        raise HTTPException(status_code=500, detail="Failed to create student profile")
    
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
```

---

### Task 4 — Build Faculty Registration Endpoint (Admin Only)

Add `POST /api/v1/auth/register/faculty`:
- Protected: requires an admin secret header `X-Admin-Secret` matching `settings.ADMIN_SECRET` from `.env`
- Same pattern as student registration but creates a Faculty row
- Required fields: email, password, full_name, employee_id, department, designation
- Add `ADMIN_SECRET=placement360_admin_2026` to `.env`

---

### Task 5 — Build Token Refresh Endpoint

Add `POST /api/v1/auth/refresh`:

```python
@router.post("/refresh")
async def refresh_token(
    refresh_token: str = Body(...),
    db: Session = Depends(get_db)
):
    """Refresh access token using Supabase refresh token"""
    
    res = requests.post(
        f"{settings.SUPABASE_URL}/auth/v1/token?grant_type=refresh_token",
        headers={
            "apikey": settings.SUPABASE_ANON_KEY,
            "Content-Type": "application/json"
        },
        json={"refresh_token": refresh_token}
    )
    
    if res.status_code != 200:
        raise HTTPException(status_code=401, detail="Invalid or expired refresh token")
    
    data = res.json()
    user_id = data["user"]["id"]
    role = data["user"].get("user_metadata", {}).get("role")
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
```

---

### Task 6 — Add `_create_local_jwt` Helper

Add this shared helper to `app/api/v1/auth.py` so both real login and mock-login use the same JWT creation logic:

```python
from datetime import datetime, timedelta
from jose import jwt

def _create_local_jwt(payload: dict) -> str:
    expire = datetime.utcnow() + timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    payload.update({"iat": datetime.utcnow(), "exp": expire, "type": "access"})
    return jwt.encode(payload, settings.SECRET_KEY, algorithm="HS256")
```

Update mock-login to use this same helper so both endpoints produce identical token format.

---

### Task 7 — Add Password Reset Endpoint

Add `POST /api/v1/auth/forgot-password`:

```python
@router.post("/forgot-password")
async def forgot_password(email: str = Body(...)):
    """Send password reset email via Supabase"""
    
    res = requests.post(
        f"{settings.SUPABASE_URL}/auth/v1/recover",
        headers={
            "apikey": settings.SUPABASE_ANON_KEY,
            "Content-Type": "application/json"
        },
        json={"email": email}
    )
    
    # Always return success to prevent email enumeration
    return {"message": "If this email is registered, a reset link has been sent"}
```

---

### Task 8 — Seed 5 Test Students + 2 Test Faculty

Create `scripts/seed_test_users.py` that creates realistic test users:

**5 Students:**
| Name | Email | Password | Roll | Branch | Year |
|---|---|---|---|---|---|
| Aarav Sharma | aarav@placement360.dev | Student@123 | CS21B001 | computer_science | fourth |
| Priya Patel | priya.p@placement360.dev | Student@123 | CS21B002 | computer_science | fourth |
| Rahul Verma | rahul@placement360.dev | Student@123 | IT21B001 | information_technology | fourth |
| Sneha Reddy | sneha@placement360.dev | Student@123 | CS22B001 | computer_science | third |
| Arjun Singh | arjun@placement360.dev | Student@123 | CS21B003 | computer_science | fourth |

**2 Faculty:**
| Name | Email | Password | Employee ID | Department |
|---|---|---|---|---|
| Dr. Priya Sharma | drpriya@placement360.dev | Faculty@123 | FAC2021001 | computer_science |
| Prof. Ravi Kumar | ravi@placement360.dev | Faculty@123 | FAC2021002 | information_technology |

Script should:
1. Create each user in Supabase Auth using admin API
2. Create their profile row in `students` or `faculty` table
3. Print success/failure for each user
4. Skip if email already exists

Run this script and paste the complete output.

---

### Verification

After all tasks, run this and paste output:

```python
import requests, os
from dotenv import load_dotenv
load_dotenv()

SUPABASE_URL = os.getenv("SUPABASE_URL")
SERVICE_KEY = os.getenv("SUPABASE_SERVICE_ROLE_KEY")
BASE = "http://localhost:8000/api/v1"

headers = {"apikey": SERVICE_KEY, "Authorization": f"Bearer {SERVICE_KEY}"}

# Check auth users count
res = requests.get(f"{SUPABASE_URL}/auth/v1/admin/users", headers=headers)
print(f"Total auth users: {len(res.json().get('users', []))}")

# Test real login
res2 = requests.post(f"{BASE}/auth/login", json={
    "email": "aarav@placement360.dev",
    "password": "Student@123"
})
print(f"Real login (student): {res2.status_code}")
if res2.status_code == 200:
    print(f"  name: {res2.json().get('name')}")
    print(f"  role: {res2.json().get('role')}")

res3 = requests.post(f"{BASE}/auth/login", json={
    "email": "drpriya@placement360.dev", 
    "password": "Faculty@123"
})
print(f"Real login (faculty): {res3.status_code}")

# Test mock login still works
res4 = requests.post(f"{BASE}/auth/mock-login", json={"role": "student"})
print(f"Mock login still works: {res4.status_code}")
```

---
