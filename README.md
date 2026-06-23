<h1 align="center">
  <br>
  🎓 Placement360 — Backend API
  <br>
</h1>

<p align="center">
  <b>A production-grade FastAPI backend powering the Placement360 campus recruitment preparation platform.</b>
</p>

<p align="center">
  <img src="https://img.shields.io/badge/FastAPI-0.115.6-009688?style=for-the-badge&logo=fastapi&logoColor=white" />
  <img src="https://img.shields.io/badge/Python-3.11+-3776AB?style=for-the-badge&logo=python&logoColor=white" />
  <img src="https://img.shields.io/badge/PostgreSQL-Supabase-3ECF8E?style=for-the-badge&logo=supabase&logoColor=white" />
  <img src="https://img.shields.io/badge/Deployed-Railway-0B0D0E?style=for-the-badge&logo=railway&logoColor=white" />
</p>

<p align="center">
  <img src="https://img.shields.io/badge/SQLAlchemy-2.0-red?style=flat-square" />
  <img src="https://img.shields.io/badge/Alembic-Migrations-blue?style=flat-square" />
  <img src="https://img.shields.io/badge/Redis-Caching-DC382D?style=flat-square&logo=redis&logoColor=white" />
  <img src="https://img.shields.io/badge/Judge0-Code%20Execution-orange?style=flat-square" />
  <img src="https://img.shields.io/badge/OpenAI-AI%20Services-412991?style=flat-square&logo=openai&logoColor=white" />
</p>

---

## 📖 Table of Contents

- [Overview](#-overview)
- [Features](#-features)
- [Tech Stack](#-tech-stack)
- [Project Structure](#-project-structure)
- [API Endpoints](#-api-endpoints)
- [Getting Started](#-getting-started)
- [Environment Variables](#-environment-variables)
- [Database & Migrations](#-database--migrations)
- [Deployment](#-deployment)
- [Authentication Flow](#-authentication-flow)

---

## 🌟 Overview

**Placement360** is a comprehensive campus placement preparation platform built for engineering students and faculty. The backend provides a robust RESTful API handling everything from user authentication and assessments to real-time code execution and AI-powered features.

> 🚀 **Live API:** Deployed on [Railway](https://railway.app) with health checks at `/api/v1/health`

---

## ✨ Features

| Category | Features |
|----------|----------|
| 🔐 **Authentication** | Supabase Auth integration, JWT tokens, role-based access (Student / Faculty / Admin) |
| 📝 **Assessments** | Mock tests, placement tests, MCQ, coding challenges, contests |
| 🧠 **Code Execution** | Judge0 integration — Python, Java, C++, JavaScript, Go, Rust, C, C# |
| 🤖 **AI Services** | OpenAI / Anthropic powered hints, explanations & feedback |
| 📊 **Analytics** | Student performance dashboards, faculty reports, progress tracking |
| 🏢 **Companies** | Company profiles, placement history management |
| 🔗 **External Platforms** | LeetCode, Codeforces, HackerRank, CodeChef, GeeksforGeeks integrations |
| 📥 **Question Import** | Bulk question import via Excel/PDF file upload |
| ⚡ **Caching** | Redis-based caching with configurable TTL |
| 🔄 **Background Tasks** | APScheduler for recurring jobs and data sync |
| 📧 **Email** | SendGrid integration for notifications |

---

## 🛠 Tech Stack

```
FastAPI 0.115.6        → High-performance async web framework
Uvicorn / Gunicorn    → ASGI server with worker management
SQLAlchemy 2.0        → Async ORM with connection pooling
Alembic               → Database schema migrations
PostgreSQL (Supabase) → Primary relational database
Redis                 → Caching layer
Pydantic v2           → Data validation & settings management
python-jose           → JWT token handling
passlib / bcrypt      → Password hashing
Judge0                → Remote code execution sandbox
OpenAI / Anthropic    → AI-powered features
SendGrid              → Transactional email
APScheduler           → Background task scheduling
httpx                 → Async HTTP client
BeautifulSoup4        → Web scraping for platform data
openpyxl / pdfplumber → File parsing for question imports
```

---

## 📁 Project Structure

```
placement360-backend/
├── app/
│   ├── main.py                  # FastAPI application entry point
│   ├── api/
│   │   └── v1/
│   │       ├── router.py        # Central API router
│   │       ├── auth.py          # Auth endpoints
│   │       ├── students.py      # Student management
│   │       ├── faculty.py       # Faculty management
│   │       ├── assessments.py   # Assessment CRUD & logic
│   │       ├── questions.py     # Question bank
│   │       ├── question_import.py # Bulk import via files
│   │       ├── submissions.py   # Code submission handling
│   │       ├── external_platforms.py # Platform integrations
│   │       ├── analytics.py     # Analytics & reports
│   │       ├── companies.py     # Company management
│   │       ├── ai.py            # AI-powered endpoints
│   │       ├── database.py      # DB health/admin
│   │       └── health.py        # Health check endpoint
│   ├── core/
│   │   ├── config.py            # Settings & environment config
│   │   ├── database.py          # DB engine & session management
│   │   ├── exceptions.py        # Custom exception handlers
│   │   ├── logging_config.py    # Structured logging setup
│   │   └── validation.py        # Config validation on startup
│   ├── models/                  # SQLAlchemy ORM models
│   │   ├── student.py
│   │   ├── faculty.py
│   │   ├── assessment.py
│   │   ├── question.py
│   │   ├── submission.py
│   │   ├── assessment_attempt.py
│   │   ├── auth_user.py
│   │   └── enums.py             # All platform enums
│   ├── schemas/                 # Pydantic request/response schemas
│   ├── crud/                    # Database CRUD operations
│   ├── services/                # Business logic layer
│   ├── integrations/            # Third-party service clients
│   ├── ml/                      # ML/AI feature modules
│   ├── tasks/                   # Background task definitions
│   └── utils/                   # Helper utilities
├── alembic/                     # Database migrations
│   └── versions/
├── docs/                        # Additional documentation
├── tests/                       # Test suite
├── .env.example                 # Environment variable template
├── .env.production.example      # Production env template
├── requirements.txt             # Python dependencies
├── Procfile                     # Heroku/Railway process definition
├── railway.toml                 # Railway deployment config
├── alembic.ini                  # Alembic migration config
└── pytest.ini                   # Test configuration
```

---

## 🔌 API Endpoints

All routes are prefixed with `/api/v1`

| Tag | Prefix | Description |
|-----|--------|-------------|
| 🏥 Health | `/health` | Server health & readiness check |
| 🔐 Authentication | `/auth` | Register, login, token refresh, logout |
| 👨‍🎓 Students | `/students` | Student profile, dashboard, progress |
| 👨‍🏫 Faculty | `/faculty` | Faculty management, student oversight |
| 📝 Assessments | `/assessments` | Create, schedule, attempt assessments |
| ❓ Questions | `/questions` | Question bank CRUD |
| 📥 Import | `/import` | Bulk question import (Excel / PDF) |
| ✅ Submissions | `/submissions` | Code submissions & Judge0 execution |
| 🔗 Platforms | `/platforms` | LeetCode / CF / HackerRank sync |
| 📊 Analytics | `/analytics` | Performance analytics & reports |
| 🏢 Companies | `/companies` | Company profile management |
| 🤖 AI Services | `/ai` | AI hints, explanations, feedback |
| 🗄 Database | `/database` | DB admin utilities (admin only) |

> 📄 Interactive API docs available at `/docs` (when `DEBUG=True`)

---

## 🚀 Getting Started

### Prerequisites

- Python 3.11+
- PostgreSQL 14+ (or Supabase project)
- Redis (optional, for caching)
- Git

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

### 4. Configure Environment Variables

```bash
cp .env.example .env
# Edit .env with your actual values
```

### 5. Run Database Migrations

```bash
alembic upgrade head
```

### 6. Start the Development Server

```bash
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

The API will be live at **http://localhost:8000** and docs at **http://localhost:8000/docs**

---

## ⚙️ Environment Variables

Copy `.env.example` to `.env` and fill in the values:

```env
# ─── Application ───────────────────────────────────
PROJECT_NAME=Placement360 Backend
VERSION=1.0.0
API_V1_STR=/api/v1
DEBUG=True
ENVIRONMENT=development         # development | staging | production

# ─── Database (Supabase PostgreSQL) ─────────────────
DATABASE_URL=postgresql://postgres.[PROJECT-REF]:[PASSWORD]@[HOST]:6543/postgres
DB_POOL_SIZE=10
DB_MAX_OVERFLOW=20
DB_POOL_TIMEOUT=30

# ─── Redis (Optional Caching) ────────────────────────
REDIS_URL=redis://default:[PASSWORD]@[HOST]:6379
CACHE_TTL_HOURS=12

# ─── Security ────────────────────────────────────────
SECRET_KEY=<generate-with: python -c "import secrets; print(secrets.token_urlsafe(48))">
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30
REFRESH_TOKEN_EXPIRE_DAYS=7

# ─── CORS ────────────────────────────────────────────
ALLOWED_ORIGINS=http://localhost:3000,http://localhost:3001

# ─── Supabase ────────────────────────────────────────
SUPABASE_URL=https://[PROJECT-REF].supabase.co
SUPABASE_KEY=<anon-key>
SUPABASE_SERVICE_ROLE_KEY=<service-role-key>

# ─── Judge0 (Code Execution) ─────────────────────────
JUDGE0_API_KEY=<rapidapi-key>
JUDGE0_HOST=judge0-ce.p.rapidapi.com

# ─── AI Services ─────────────────────────────────────
AI_PROVIDER=openai              # openai | anthropic
OPENAI_API_KEY=sk-proj-...
OPENAI_MODEL=gpt-4o-mini
ANTHROPIC_API_KEY=sk-ant-...    # Optional

# ─── Email (SendGrid) ────────────────────────────────
SENDGRID_API_KEY=SG....
SENDGRID_FROM_EMAIL=noreply@yourapp.com

# ─── External Platforms (Optional) ───────────────────
LEETCODE_SESSION=<session-cookie>
GITHUB_CLIENT_ID=<oauth-app-id>
GITHUB_CLIENT_SECRET=<oauth-secret>

# ─── Rate Limiting ────────────────────────────────────
RATE_LIMIT_PER_MINUTE=100
LOG_LEVEL=INFO
```

> 🔒 **Never commit your `.env` file!** It's listed in `.gitignore`.

---

## 🗄 Database & Migrations

The project uses **Alembic** for schema migrations against a **Supabase PostgreSQL** database.

```bash
# Apply all pending migrations
alembic upgrade head

# Create a new migration
alembic revision --autogenerate -m "describe your change"

# Downgrade one step
alembic downgrade -1

# View migration history
alembic history
```

### Data Models

| Model | Description |
|-------|-------------|
| `Student` | Student profile, branch, year, CGPA, coding stats |
| `Faculty` | Faculty profile, department, designation |
| `AuthUser` | Auth identity linked to Supabase Auth |
| `Assessment` | Test metadata, type, schedule, duration |
| `AssessmentAttempt` | Student attempt records with scores |
| `Question` | Question bank (MCQ, Coding, Subjective) |
| `AssessmentQuestion` | Question ↔ Assessment mapping with order |
| `Submission` | Code submission & Judge0 execution result |
| `QuestionImportJob` | Async bulk import job tracking |

---

## 🚢 Deployment

### Railway (Recommended)

The project includes a pre-configured [`railway.toml`](railway.toml):

```toml
[build]
builder = "NIXPACKS"

[deploy]
startCommand = "gunicorn app.main:app --workers 2 --worker-class uvicorn.workers.UvicornWorker --bind 0.0.0.0:$PORT --timeout 120"
restartPolicyType = "ON_FAILURE"
restartPolicyMaxRetries = 3

[deploy.healthcheck]
path = "/api/v1/health"
timeoutSeconds = 30
intervalSeconds = 10
```

**Steps:**
1. Connect your GitHub repository to [Railway](https://railway.app)
2. Add all required environment variables in Railway dashboard
3. Railway auto-deploys on every push to `main`

### Heroku / Render

Use the included `Procfile`:

```
web: gunicorn app.main:app --workers 2 --worker-class uvicorn.workers.UvicornWorker --bind 0.0.0.0:$PORT --timeout 120
```

---

## 🔐 Authentication Flow

```
Client                    Backend                    Supabase
  │                          │                           │
  │─── POST /auth/login ────►│                           │
  │                          │── Verify credentials ────►│
  │                          │◄── JWT token ─────────────│
  │◄─── access_token ────────│                           │
  │                          │                           │
  │─── GET /api/v1/... ─────►│                           │
  │    Authorization: Bearer │                           │
  │                          │── Validate JWT ──────────►│
  │                          │◄── User identity ─────────│
  │◄─── Protected response ──│                           │
```

### Roles & Permissions

| Role | Access Level |
|------|-------------|
| `student` | Own profile, assessments, submissions, platforms |
| `faculty` | Student management, assessment creation, analytics |
| `admin` | Full access including database admin endpoints |

---

## 🧪 Running Tests

```bash
# Run all tests
pytest

# Run with coverage report
pytest --cov=app --cov-report=html

# Run a specific test file
pytest tests/test_assessments.py -v
```

---

## 📦 Key Dependencies

| Package | Version | Purpose |
|---------|---------|---------|
| `fastapi` | 0.115.6 | Web framework |
| `uvicorn[standard]` | 0.27.0 | ASGI server |
| `gunicorn` | 21.2.0 | Production process manager |
| `sqlalchemy` | 2.0.36 | ORM |
| `alembic` | 1.14.0 | Migrations |
| `psycopg2-binary` | 2.9.10 | PostgreSQL driver |
| `supabase` | 2.13.0 | Supabase client |
| `python-jose[cryptography]` | 3.3.0 | JWT handling |
| `passlib[bcrypt]` | 1.7.4 | Password hashing |
| `redis` | 5.2.1 | Redis client |
| `apscheduler` | 3.11.2 | Background task scheduling |
| `httpx` | 0.28.1 | Async HTTP client |
| `pdfplumber` | 0.11.5 | PDF parsing |
| `openpyxl` | 3.1.5 | Excel file parsing |
| `beautifulsoup4` | 4.14.3 | Web scraping |

---

## 🤝 Contributing

1. Fork the repository
2. Create your feature branch: `git checkout -b feature/amazing-feature`
3. Commit your changes: `git commit -m 'feat: add amazing feature'`
4. Push to the branch: `git push origin feature/amazing-feature`
5. Open a Pull Request

---

## 📄 License

This project is part of the Placement360 platform. All rights reserved.

---

<p align="center">
  Built with ❤️ for engineering students preparing for campus placements
</p>
