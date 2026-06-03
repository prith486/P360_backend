from fastapi import APIRouter, HTTPException, status, Request
from pydantic import BaseModel
from typing import Optional
import uuid

router = APIRouter()

# --- Request Models ---

class SignupRequest(BaseModel):
    email: str
    password: str
    confirmPassword: str
    firstName: str
    lastName: str
    role: str  # "student" | "faculty"
    department: Optional[str] = None
    university: Optional[str] = None

class LoginRequest(BaseModel):
    email: str
    password: str

# --- Routes ---

@router.post("/api/auth/signup", status_code=status.HTTP_201_CREATED)
async def signup(data: SignupRequest):
    # Mock logic: Check if user exists (mocked as always new for now)
    
    # Generate mock user data
    user_id = str(uuid.uuid4())
    
    # Return strict JSON structure
    return {
        "success": True,
        "data": {
            "user": {
                "id": user_id,
                "email": data.email,
                "firstName": data.firstName,
                "lastName": data.lastName,
                "role": data.role
            },
            "accessToken": "mock_valid_jwt_token_" + user_id,
            "refreshToken": "mock_valid_refresh_token_" + user_id
        }
    }

@router.post("/api/auth/login", status_code=status.HTTP_200_OK)
async def login(data: LoginRequest):
    # Mock logic: Accept ANY credentials for easier testing
    role = "student"
    if "faculty" in data.email.lower() or "professor" in data.email.lower():
        role = "faculty"
        
    # Hardcoded test UUIDs
    # Student: 00000000-0000-0000-0000-000000000001
    # Faculty: 00000000-0000-0000-0000-000000000002
    user_id = "00000000-0000-0000-0000-000000000001" if role == "student" else "00000000-0000-0000-0000-000000000002"
    
    return {
        "success": True,
        "data": {
            "user": {
                "id": user_id,
                "email": data.email,
                "firstName": "Test",
                "lastName": "Student" if role == "student" else "Faculty",
                "role": role
            },
            # Return both formats for maximum compatibility
            "accessToken": f"mock_valid_{role}_token_{user_id}",
            "access_token": f"mock_valid_{role}_token_{user_id}",
            "token_type": "bearer",
            "refreshToken": f"mock_valid_{role}_refresh_token_{user_id}"
        }
    }

@router.get("/api/auth/me")
async def get_current_user_info(request: Request):
    auth_header = request.headers.get("Authorization", "")
    role = "student"
    user_id = "00000000-0000-0000-0000-000000000001"
    
    if "faculty" in auth_header.lower():
        role = "faculty"
        user_id = "00000000-0000-0000-0000-000000000002"
        
    return {
        "success": True,
        "data": {
            "id": user_id,
            "email": f"test@{role}.com",
            "firstName": "Test",
            "lastName": "Student" if role == "student" else "Faculty",
            "role": role,
            "department": "Computer Science",
            "university": "Test University",
            "avatarUrl": None,
            "isVerified": True
        }
    }

@router.post("/api/auth/logout")
async def logout():
    return {
        "success": True,
        "message": "Logged out successfully"
    }

@router.get("/api/student/dashboard")
async def mock_student_dashboard():
    # Mock data structure matching the real dashboard logic
    return {
        "success": True,
        "data": {
            "profile": {
                "id": "1",
                "firstName": "Test",
                "lastName": "User",
                "email": "test@test.com",
                "rollNumber": "CS2024001",
                "branch": "Computer Science",
                "year": "3rd",
                "avatarUrl": None
            },
            "stats": {
                "problemsSolved": 42,
                "totalProblems": 150,
                "currentStreak": 5,
                "longestStreak": 12,
                "rank": 15,
                "branchRank": 3,
                "totalScore": 850
            },
            "recentSubmissions": [
                {
                    "id": "sub1",
                    "problemTitle": "Two Sum",
                    "difficulty": "Easy",
                    "status": "Accepted",
                    "language": "Python",
                    "submittedAt": "2024-02-15T10:30:00Z",
                    "score": 100
                },
                {
                    "id": "sub2",
                    "problemTitle": "Reverse Linked List",
                    "difficulty": "Medium",
                    "status": "Wrong Answer",
                    "language": "Java",
                    "submittedAt": "2024-02-14T15:20:00Z",
                    "score": 0
                }
            ],
            "upcomingAssessments": [
                {
                    "id": "asm1",
                    "title": "Data Structures Mid-Term",
                    "startTime": "2024-03-01T09:00:00Z",
                    "endTime": "2024-03-01T12:00:00Z",
                    "duration": 180,
                    "type": "Exam",
                    "totalQuestions": 25
                }
            ],
            "skillProgress": {
                "Arrays": 80,
                "Dynamic Programming": 45,
                "Graphs": 60,
                "Strings": 90
            }
        }
    }

@router.get("/api/faculty/dashboard")
async def mock_faculty_dashboard():
    # Mock data for Faculty Dashboard
    return {
        "success": True,
        "data": {
            "profile": {
                "id": "1",
                "firstName": "Faculty",
                "lastName": "Member",
                "email": "faculty@test.com",
                "department": "Computer Science",
                "designation": "Senior Professor",
                "avatarUrl": None
            },
            "stats": {
                "totalStudents": 120,
                "activeAssessments": 3,
                "questionsCreated": 45,
                "pendingEvaluations": 12
            },
            "recentAssessments": [
                {
                    "id": "asm1",
                    "title": "Data Structures Mid-Term",
                    "course": "CS202",
                    "status": "Active",
                    "startTime": "2024-03-01T09:00:00Z",
                    "submissions": 45,
                    "totalStudents": 60
                },
                {
                    "id": "asm2",
                    "title": "Algorithms Quiz 1",
                    "course": "CS301",
                    "status": "Completed",
                    "startTime": "2024-02-10T10:00:00Z",
                    "submissions": 58,
                    "totalStudents": 60
                }
            ],
            "studentPerformance": {
                "averageScore": 76.5,
                "topPerformers": [
                    {"id": "s1", "name": "Alice Johnson", "rollNumber": "CS001", "score": 98},
                    {"id": "s2", "name": "Bob Smith", "rollNumber": "CS005", "score": 95}
                ],
                "needsAttention": [
                    {"id": "s3", "name": "Charlie Brown", "rollNumber": "CS023", "score": 45},
                    {"id": "s4", "name": "David Wilson", "rollNumber": "CS041", "score": 52}
                ]
            },
            "recentActivity": []
        }
    }
