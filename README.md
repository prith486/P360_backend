# Placement360 — Backend API

[![FastAPI](https://img.shields.io/badge/FastAPI-0.115.6-009688?style=flat-square&logo=fastapi&logoColor=white)](https://fastapi.tiangolo.com)
[![Python](https://img.shields.io/badge/Python-3.11+-3776AB?style=flat-square&logo=python&logoColor=white)](https://python.org)
[![PostgreSQL](https://img.shields.io/badge/PostgreSQL-Supabase-3ECF8E?style=flat-square&logo=supabase&logoColor=white)](https://supabase.com)
[![Deployed on Railway](https://img.shields.io/badge/Deployed-Railway-0B0D0E?style=flat-square&logo=railway&logoColor=white)](https://railway.app)
[![License](https://img.shields.io/badge/License-Proprietary-red?style=flat-square)]()

Production-grade REST API backend for the Placement360 campus recruitment preparation platform. Built with FastAPI, PostgreSQL (Supabase), and Redis.

---

## Table of Contents

- [Overview](#overview)
- [Features](#features)
- [Tech Stack](#tech-stack)
- [Project Structure](#project-structure)
- [API Reference](#api-reference)
- [Getting Started](#getting-started)
- [Environment Variables](#environment-variables)
- [Database & Migrations](#database--migrations)
- [Deployment](#deployment)
- [Authentication](#authentication)
- [Testing](#testing)

---

## Overview

Placement360 is a platform designed to help engineering students prepare for campus placements. The backend exposes a versioned REST API (`/api/v1`) that handles user authentication, assessments, question banks, real-time code execution via Judge0, AI-powered assistance, and analytics.

> **Live API Base URL:** `https://<your-railway-domain>/api/v1`
> **Health Check:** `GET /api/v1/health`

---

## Features

| Category | Details |
|---|---|
| Authentication | Supabase Auth integration, JWT tokens, role-based access control (Student / Faculty / Admin) |
| Assessments | Mock tests, placement tests, MCQ, coding challenges, contests with scheduling support |
| Code Execution | Judge0 sandbox — Python, Java, C++, JavaScript, Go, Rust, C, C# |
| AI Services | OpenAI and Anthropic-powered hints, explanations, and personalized feedback |
| Analytics | Student performance dashboards, faculty-level reports, progress tracking |
| Companies | Company profile and placement history management |
| External Platforms | LeetCode, Codeforces, HackerRank, CodeChef, GeeksforGeeks data sync |
| Question Import | Bulk question upload via Excel (.xlsx) and PDF files |
| Caching | Redis-based caching with configurable TTL |
| Background Tasks | APScheduler for recurring sync jobs and scheduled operations |
| Email | SendGrid integration for transactional notifications |

---

## Tech Stack

| Layer | Technology |
|---|---|
| Framework | FastAPI 0.115.6 |
| Server | Uvicorn (dev), Gunicorn + UvicornWorker (prod) |
| ORM | SQLAlchemy 2.0 |
| Migrations | Alembic |
| Database | PostgreSQL via Supabase |
| Cache | Redis |
| Auth | Supabase Auth + python-jose (JWT) |
| Password Hashing | passlib / bcrypt |
| Code Execution | Judge0 (RapidAPI) |
| AI | OpenAI API / Anthropic Claude |
| Email | SendGrid |
| Task Scheduling | APScheduler |
| HTTP Client | httpx |
| File Parsing | openpyxl, pdfplumber |
| Web Scraping | BeautifulSoup4 |
| Validation | Pydantic v2 |

---

## Project Structure

```
placement360-backend/
├── app/
│   ├── main.py                      # Application entry point, lifespan, middleware
│   ├── api/
│   │   └── v1/
│   │       ├── router.py            # Central API router
│   │       ├── auth.py              # Registration, login, token refresh
│   │       ├── students.py          # Student profile and management
│   │       ├── faculty.py           # Faculty management
│   │       ├── assessments.py       # Assessment CRUD, scheduling, attempts
│   │       ├── questions.py         # Question bank CRUD
│   │       ├── question_import.py   # Bulk import via Excel/PDF
│   │       ├── submissions.py       # Code submission and Judge0 execution
│   │       ├── external_platforms.py # Platform data sync
│   │       ├── analytics.py         # Performance analytics
│   │       ├── companies.py         # Company management
│   │       ├── ai.py                # AI-powered endpoints
│   │       ├── database.py          # DB admin utilities
│   │       └── health.py            # Health check
│   ├── core/
│   │   ├── config.py                # Pydantic settings, env var parsing
│   │   ├── database.py              # Engine setup, session factory
│   │   ├── exceptions.py            # Global exception handlers
│   │   ├── logging_config.py        # Structured logging
│   │   └── validation.py            # Startup config validation
│   ├── models/                      # SQLAlchemy ORM models
│   │   ├── student.py
│   │   ├── faculty.py
│   │   ├── assessment.py
│   │   ├── assessment_attempt.py
│   │   ├── assessment_question.py
│   │   ├── question.py
│   │   ├── question_import_job.py
│   │   ├── submission.py
│   │   ├── auth_user.py
│   │   └── enums.py
│   ├── schemas/                     # Pydantic request/response models
│   ├── crud/                        # Database access layer
│   ├── services/                    # Business logic
│   ├── integrations/                # Third-party API clients
│   ├── ml/                          # ML and AI feature modules
│   ├── tasks/                       # Background task definitions
│   └── utils/                       # Shared utilities
├── alembic/
│   └── versions/                    # Migration files
├── docs/                            # Additional documentation
├── tests/                           # Test suite
├── scripts/                         # Utility scripts
├── .env.example                     # Environment variable template
├── .env.production.example          # Production environment template
├── requirements.txt
├── Procfile                         # Process definition for Railway/Heroku
├── railway.toml                     # Railway deployment configuration
├── alembic.ini
└── pytest.ini
```

---

## API Reference

All routes are prefixed with `/api/v1`. Interactive docs are available at `/docs` when `DEBUG=True`.

| Tag | Prefix | Description |
|---|---|---|
| Health | `/health` | Server health and readiness |
| Authentication | `/auth` | Register, login, token refresh, logout |
| Students | `/students` | Profile, dashboard, progress tracking |
| Faculty | `/faculty` | Faculty management, student oversight |
| Assessments | `/assessments` | Create, schedule, and attempt assessments |
| Questions | `/questions` | Question bank CRUD |
| Import | `/import` | Bulk question import from Excel/PDF |
| Submissions | `/submissions` | Code submissions and execution results |
| Platforms | `/platforms` | External coding platform data sync |
| Analytics | `/analytics` | Performance reports and dashboards |
| Companies | `/companies` | Company profile management |
| AI Services | `/ai` | AI hints, explanations, and feedback |
| Database | `/database` | Admin database utilities |

---

## Getting Started

### Prerequisites

- Python 3.11 or higher
- PostgreSQL 14+ (or a Supabase project)
- Redis (optional, for caching)

### 1. Clone the Repository

```bash
git clone https://github.com/prith486/P360_backend.git
cd P360_backend
```

### 2. Create a Virtual Environment

```bash
python -m venv venv

# Windows
venv\Scripts\activate

# macOS / Linux
source venv/bin/activate
```

### 3. Install Dependencies

```bash
pip install -r requirements.txt
```

### 4. Configure Environment

```bash
cp .env.example .env
# Open .env and fill in the required values
```

### 5. Run Database Migrations

```bash
alembic upgrade head
```

### 6. Start the Development Server

```bash
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

The API is available at `http://localhost:8000` and the interactive docs at `http://localhost:8000/docs`.

---

## Environment Variables

Copy `.env.example` to `.env` and populate it:

```env
# Application
PROJECT_NAME=Placement360 Backend
VERSION=1.0.0
API_V1_STR=/api/v1
DEBUG=True
ENVIRONMENT=development          # development | staging | production

# Database
DATABASE_URL=postgresql://postgres.[PROJECT-REF]:[PASSWORD]@[HOST]:6543/postgres
DB_POOL_SIZE=10
DB_MAX_OVERFLOW=20
DB_POOL_TIMEOUT=30

# Redis (optional)
REDIS_URL=redis://default:[PASSWORD]@[HOST]:6379
CACHE_TTL_HOURS=12

# Security
# Generate: python -c "import secrets; print(secrets.token_urlsafe(48))"
SECRET_KEY=<generate-a-strong-secret>
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30
REFRESH_TOKEN_EXPIRE_DAYS=7

# CORS
ALLOWED_ORIGINS=http://localhost:3000,http://localhost:3001

# Supabase
SUPABASE_URL=https://[PROJECT-REF].supabase.co
SUPABASE_KEY=<anon-public-key>
SUPABASE_SERVICE_ROLE_KEY=<service-role-key>

# Judge0 (Code Execution)
JUDGE0_API_KEY=<rapidapi-key>
JUDGE0_HOST=judge0-ce.p.rapidapi.com

# AI Services
AI_PROVIDER=openai               # openai | anthropic
OPENAI_API_KEY=sk-proj-...
OPENAI_MODEL=gpt-4o-mini
ANTHROPIC_API_KEY=sk-ant-...     # Optional

# Email
SENDGRID_API_KEY=SG....
SENDGRID_FROM_EMAIL=noreply@yourapp.com

# External Platforms (optional)
LEETCODE_SESSION=<session-cookie>
GITHUB_CLIENT_ID=<oauth-app-id>
GITHUB_CLIENT_SECRET=<oauth-secret>

# Rate Limiting and Logging
RATE_LIMIT_PER_MINUTE=100
LOG_LEVEL=INFO
```

> **Note:** Never commit your `.env` file. It is excluded via `.gitignore`.

---

## Database & Migrations

Alembic is used for schema migrations against the Supabase PostgreSQL instance.

```bash
# Apply all pending migrations
alembic upgrade head

# Create a new migration after model changes
alembic revision --autogenerate -m "describe change"

# Rollback one step
alembic downgrade -1

# View migration history
alembic history
```

### Data Models

| Model | Description |
|---|---|
| `Student` | Student profile: branch, academic year, CGPA, platform stats |
| `Faculty` | Faculty profile: department, designation |
| `AuthUser` | Auth identity linked to Supabase Auth |
| `Assessment` | Test metadata: type, schedule, duration, visibility |
| `AssessmentAttempt` | Per-student attempt record with score and status |
| `AssessmentQuestion` | Question-to-Assessment mapping with ordering |
| `Question` | Question bank entry (MCQ, Coding, Subjective) |
| `Submission` | Code submission record with Judge0 execution result |
| `QuestionImportJob` | Async bulk import job tracking |

---

## Deployment

### Railway

The repository includes a pre-configured `railway.toml`:

```toml
[build]
builder = "NIXPACKS"

[deploy]
startCommand = "gunicorn app.main:app --workers 2 --worker-class uvicorn.workers.UvicornWorker --bind 0.0.0.0:$PORT --timeout 120 --keepalive 5"
restartPolicyType = "ON_FAILURE"
restartPolicyMaxRetries = 3

[deploy.healthcheck]
path = "/api/v1/health"
timeoutSeconds = 30
intervalSeconds = 10
```

**Steps:**
1. Connect this repository to a Railway project.
2. Set all required environment variables in the Railway dashboard.
3. Railway will auto-deploy on every push to `main`.

### Heroku / Render

Use the included `Procfile`:

```
web: gunicorn app.main:app --workers 2 --worker-class uvicorn.workers.UvicornWorker --bind 0.0.0.0:$PORT --timeout 120 --keepalive 5
```

---

## Authentication

The platform uses Supabase Auth for identity management combined with JWT tokens for API request authorization.

```
Client                     Backend                    Supabase Auth
  |                           |                             |
  |--- POST /auth/login ------>|                             |
  |                           |--- Verify credentials ------>|
  |                           |<--- JWT token ---------------| 
  |<--- access_token ----------|                             |
  |                           |                             |
  |--- GET /api/v1/... ------->|                             |
  |    Authorization: Bearer  |                             |
  |                           |--- Validate JWT ------------>|
  |                           |<--- User identity -----------|
  |<--- Protected response ----|                             |
```

### Roles

| Role | Access |
|---|---|
| `student` | Own profile, assessments, submissions, platform data |
| `faculty` | Student management, assessment creation, analytics |
| `admin` | Full platform access including database admin endpoints |

---

## Testing

```bash
# Run all tests
pytest

# Run with coverage report
pytest --cov=app --cov-report=html

# Run a specific test module
pytest tests/test_assessments.py -v
```

---

## Dependencies

| Package | Version | Purpose |
|---|---|---|
| `fastapi` | 0.115.6 | Web framework |
| `uvicorn[standard]` | 0.27.0 | ASGI server |
| `gunicorn` | 21.2.0 | Production process manager |
| `sqlalchemy` | 2.0.36 | ORM |
| `alembic` | 1.14.0 | Database migrations |
| `psycopg2-binary` | 2.9.10 | PostgreSQL driver |
| `supabase` | 2.13.0 | Supabase client |
| `python-jose[cryptography]` | 3.3.0 | JWT handling |
| `passlib[bcrypt]` | 1.7.4 | Password hashing |
| `redis` | 5.2.1 | Caching layer |
| `apscheduler` | 3.11.2 | Background task scheduling |
| `httpx` | 0.28.1 | Async HTTP client |
| `pdfplumber` | 0.11.5 | PDF parsing |
| `openpyxl` | 3.1.5 | Excel file parsing |
| `beautifulsoup4` | 4.14.3 | Web scraping |
| `pydantic` | 2.10.4 | Data validation |
| `pydantic-settings` | 2.1.0 | Settings management |

---

## License

This project is part of the Placement360 platform. All rights reserved.
