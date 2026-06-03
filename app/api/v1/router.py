from fastapi import APIRouter
from app.api.v1 import (
    health,
    auth,
    mock_auth,
    students,
    faculty,
    questions,
    question_import,
    assessments,
    submissions,
    external_platforms,
    analytics,
    companies,
    ai,
    database,
    test_items,
)

api_router = APIRouter()

# Public endpoints (no authentication required)
api_router.include_router(health.router, tags=["Health"])
api_router.include_router(database.router, prefix="/database", tags=["Database"])
api_router.include_router(test_items.router, prefix="/test-items", tags=["Test Items"])
api_router.include_router(auth.router, prefix="/auth", tags=["Authentication"])
api_router.include_router(mock_auth.router, prefix="/auth", tags=["Mock Auth (Dev Only)"])

# Protected endpoints (authentication required)
api_router.include_router(students.router, prefix="/students", tags=["Students"])
api_router.include_router(faculty.router, prefix="/faculty", tags=["Faculty"])
api_router.include_router(questions.router, prefix="/questions", tags=["Questions"])
api_router.include_router(question_import.router, prefix="/import", tags=["Import"])
api_router.include_router(assessments.router, prefix="/assessments", tags=["Assessments"])
api_router.include_router(submissions.router, prefix="/submissions", tags=["Submissions"])
api_router.include_router(external_platforms.router, prefix="/platforms", tags=["External Platforms"])
api_router.include_router(analytics.router, prefix="/analytics", tags=["Analytics"])
api_router.include_router(companies.router, prefix="/companies", tags=["Companies"])
api_router.include_router(ai.router, prefix="/ai", tags=["AI Services"])
