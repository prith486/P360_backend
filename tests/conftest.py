import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool
from app.main import app
from app.core.database import Base, get_db
from app.core.config import settings

# Test database URL (separate from production)
# Use in-memory SQLite for faster tests
TEST_DATABASE_URL = "sqlite:///:memory:"

engine = create_engine(
    TEST_DATABASE_URL,
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


@pytest.fixture(scope="function")
def db():
    """Create fresh database for each test."""
    Base.metadata.create_all(bind=engine)
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()
        Base.metadata.drop_all(bind=engine)


@pytest.fixture(scope="function")
def client(db):
    """FastAPI test client with database override."""
    def override_get_db():
        try:
            yield db
        finally:
            pass
    
    app.dependency_overrides[get_db] = override_get_db
    with TestClient(app) as test_client:
        yield test_client
    app.dependency_overrides.clear()


@pytest.fixture
def create_test_user(db):
    """Factory fixture for creating test users."""
    from app.models.user import User
    from app.core.security import get_password_hash
    
    def _create_user(email: str, password: str, role: str = "student"):
        # Note: 'role' field will be added to User model later.
        # Ensure User model has this field before using this factory.
        user = User(
            email=email,
            hashed_password=get_password_hash(password),
            # role=role, # Commented out until role column exists
            is_active=True
        )
        db.add(user)
        db.commit()
        db.refresh(user)
        return user
    
    return _create_user
