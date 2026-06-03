from typing import List, Optional, Literal
from pydantic import Field, field_validator, EmailStr
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """
    Application settings loaded from environment variables.
    """
    model_config = SettingsConfigDict(
        env_file=".env",
        case_sensitive=True,
        extra="ignore"
    )
    
    # APPLICATION SETTINGS
    PROJECT_NAME: str = "Placement360 Backend"
    VERSION: str = "1.0.0"
    API_V1_STR: str = "/api/v1"
    DEBUG: bool = True
    ENVIRONMENT: Literal["development", "staging", "production"] = "development"
    
    # DATABASE CONFIGURATION
    DATABASE_URL: str = Field(
        default="postgresql://postgres.imjmjqboggaoyjdktnau:hkhrjspjgspkj@aws-1-ap-northeast-2.pooler.supabase.com:5432/postgres",
        description="PostgreSQL connection string (use pooler for production)"
    )
    DB_POOL_SIZE: int = Field(
        default=10,
        description="Number of connections to keep in the pool"
    )
    DB_MAX_OVERFLOW: int = Field(
        default=20,
        description="Max connections beyond pool_size under load"
    )
    DB_POOL_TIMEOUT: int = Field(
        default=30,
        description="Seconds to wait for connection from pool"
    )
    DB_POOL_RECYCLE: int = Field(
        default=3600,
        description="Recycle connections after this many seconds"
    )
    DB_ECHO: bool = Field(
        default=False,
        description="Log all SQL statements (use in development only)"
    )

    @field_validator("DATABASE_URL")
    @classmethod
    def validate_database_url(cls, v: str) -> str:
        if not v.startswith("postgresql"):
            raise ValueError("DATABASE_URL must start with postgresql://")
        return v
    
    @property
    def database_config(self) -> dict:
        """Get database configuration summary."""
        return {
            "pool_size": self.DB_POOL_SIZE,
            "max_overflow": self.DB_MAX_OVERFLOW,
            "pool_timeout": self.DB_POOL_TIMEOUT,
            "pool_recycle": self.DB_POOL_RECYCLE,
            "echo": self.DB_ECHO
        }
    
    # REDIS
    REDIS_URL: Optional[str] = Field(None, description="Redis connection string")
    CACHE_TTL_HOURS: int = 12
    REDIS_DECODE_RESPONSES: bool = True
    
    # SUPABASE
    # API URL (derived from project ID in connection string)
    SUPABASE_URL: Optional[str] = "https://imjmjqboggaoyjdktnau.supabase.co"
    SUPABASE_KEY: Optional[str] = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6Imltam1qcWJvZ2dhb3lqZGt0bmF1Iiwicm9sZSI6ImFub24iLCJpYXQiOjE3NzA3MDgwNDcsImV4cCI6MjA4NjI4NDA0N30.fXOio3VuTtj4WsptTcWCy1dfaVV0-P5xqRy3tFkpJC4"
    SUPABASE_SERVICE_ROLE_KEY: Optional[str] = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6Imltam1qcWJvZ2dhb3lqZGt0bmF1Iiwicm9sZSI6InNlcnZpY2Vfcm9sZSIsImlhdCI6MTc3MDcwODA0NywiZXhwIjoyMDg2Mjg0MDQ3fQ.4xBMTmFDCK3jCLGw2vHCD5sHWuv1HA2VAtHC5g_Mwvw"
    
    # SECURITY
    # In production: set SECRET_KEY to a 64-char random string via Railway env vars
    # Generate: python -c "import secrets; print(secrets.token_urlsafe(48))"
    SECRET_KEY: str = "dev-only-placeholder-key-32chars-change-in-prod-!!!"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    REFRESH_TOKEN_EXPIRE_DAYS: int = 7
    BCRYPT_ROUNDS: int = 12
    ADMIN_SECRET: str = "placement360_admin_2026"
    
    # CORS
    ALLOWED_ORIGINS: str = "http://localhost:3000,http://localhost:3001"
    ALLOW_CREDENTIALS: bool = True

    # DEVELOPMENT / MOCK AUTH
    # Set to True ONLY in local development to avoid Supabase rate limits.
    # Always keep False in staging / production.
    ENABLE_MOCK_AUTH: bool = Field(
        default=False,
        description="Enable /auth/mock-login endpoint (dev only)"
    )
    
    @property
    def allowed_origins_list(self) -> List[str]:
        return [origin.strip() for origin in self.ALLOWED_ORIGINS.split(",")]
    
    # JUDGE0
    JUDGE0_API_KEY: Optional[str] = Field(None, description="RapidAPI Judge0 key")
    JUDGE0_HOST: str = "judge0-ce.p.rapidapi.com"
    JUDGE0_USE_HTTPS: bool = True
    JUDGE0_MAX_WAIT_TIME: int = 10
    JUDGE0_MAX_CPU_TIME: int = 5
    JUDGE0_MAX_MEMORY_KB: int = 524288
    
    @property
    def judge0_base_url(self) -> str:
        protocol = "https" if self.JUDGE0_USE_HTTPS else "http"
        return f"{protocol}://{self.JUDGE0_HOST}"
    
    # AI SERVICES
    AI_PROVIDER: Literal["openai", "anthropic", "claude"] = "openai"
    OPENAI_API_KEY: Optional[str] = None
    OPENAI_BASE_URL: str = "https://api.openai.com/v1"
    OPENAI_MODEL: str = "gpt-4o-mini"
    ANTHROPIC_API_KEY: Optional[str] = None
    ANTHROPIC_MODEL: str = "claude-3-haiku-20240307"
    AI_MAX_REQUESTS_PER_DAY: int = 100
    
    # SENDGRID
    SENDGRID_API_KEY: Optional[str] = Field(None, description="SendGrid API key")
    SENDGRID_FROM_EMAIL: Optional[EmailStr] = Field(None, description="Verified sender email")
    SENDGRID_FROM_NAME: str = "Placement360 Platform"
    
    # EXTERNAL PLATFORMS
    LEETCODE_SESSION: Optional[str] = None
    LEETCODE_API_URL: str = "https://leetcode.com/graphql"
    
    CODEFORCES_API_KEY: Optional[str] = None
    CODEFORCES_API_SECRET: Optional[str] = None
    CODEFORCES_API_URL: str = "https://codeforces.com/api"
    
    HACKERRANK_BASE_URL: str = "https://www.hackerrank.com"
    CODECHEF_BASE_URL: str = "https://www.codechef.com"
    GEEKSFORGEEKS_BASE_URL: str = "https://www.geeksforgeeks.org"
    
    GITHUB_CLIENT_ID: Optional[str] = None
    GITHUB_CLIENT_SECRET: Optional[str] = None
    GITHUB_ACCESS_TOKEN: Optional[str] = None
    
    # Scraping configuration
    PLATFORM_FETCH_DELAY_SECONDS: int = 2
    PLATFORM_MAX_RETRIES: int = 3
    
    # PERFORMANCE
    RATE_LIMIT_PER_MINUTE: int = 100
    
    # LOGGING
    LOG_LEVEL: str = "INFO"
    
    # FILES
    MAX_UPLOAD_SIZE_MB: int = 10
    ALLOWED_FILE_EXTENSIONS: str = "pdf,doc,docx,jpg,png,jpeg"
    
    @property
    def allowed_extensions_list(self) -> List[str]:
        return [ext.strip() for ext in self.ALLOWED_FILE_EXTENSIONS.split(",")]
        
    @property
    def is_production(self) -> bool:
        return self.ENVIRONMENT == "production"

settings = Settings()
