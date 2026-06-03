from typing import Generator, Optional, List, Callable, Any
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session
from jose import JWTError, jwt
from app.core.database import SessionLocal
from app.core.config import settings
from app.models.user import User

# OAuth2 scheme for JWT token
oauth2_scheme = OAuth2PasswordBearer(tokenUrl=f"{settings.API_V1_STR}/auth/login")


def get_db() -> Generator:
    """
    Database session dependency.
    Yields database session and ensures cleanup.
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


async def get_current_user(
    db: Session = Depends(get_db),
    token: str = Depends(oauth2_scheme)
) -> User:
    """
    Get current authenticated user from JWT token.
    
    Raises:
        HTTPException: If token is invalid or user not found.
    """
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    
    try:
        payload = jwt.decode(
            token,
            settings.SECRET_KEY,
            algorithms=[settings.ALGORITHM]
        )
        user_id: str = payload.get("sub")
        if user_id is None:
            raise credentials_exception
    except JWTError:
        raise credentials_exception
    
    user = db.query(User).filter(User.id == int(user_id)).first()
    if user is None:
        raise credentials_exception
    
    return user


async def get_current_active_user(
    current_user: User = Depends(get_current_user)
) -> User:
    """
    Get current active user (not disabled).
    
    Raises:
        HTTPException: If user is inactive.
    """
    if not current_user.is_active:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Inactive user"
        )
    return current_user


def require_role(allowed_roles: List[str]) -> Callable[[User], Any]:
    """
    Dependency factory for role-based access control.
    
    Args:
        allowed_roles: List of allowed role names (e.g., ["admin", "faculty"])
    
    Returns:
        Dependency function that checks user role.
    """
    async def role_checker(
        current_user: User = Depends(get_current_active_user)
    ) -> User:
        # Note: role field will be added to User model in later chunks
        # This implementation assumes the User model will have a 'role' attribute
        # For now, we'll need to handle the potential AttributeError or add the field
        if not hasattr(current_user, 'role') or current_user.role not in allowed_roles:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Access denied. Required roles: {', '.join(allowed_roles)}"
            )
        return current_user
    
    return role_checker


# Common role dependencies
require_admin = require_role(["admin"])
require_faculty = require_role(["admin", "faculty"])
require_student = require_role(["student"])
