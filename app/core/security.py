"""
Security utilities for password hashing and JWT token handling.
"""

from datetime import datetime, timedelta
from typing import Optional, Any, Union

from jose import jwt
from passlib.context import CryptContext

from app.core.config import settings

# Password hashing context using bcrypt
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """
    Verify a plain password against the hashed version.
    
    Args:
        plain_password: The password in plain text
        hashed_password: The bcrypt hashed password
        
    Returns:
        True if password matches, False otherwise
    """
    return pwd_context.verify(plain_password, hashed_password)


def get_password_hash(password: str) -> str:
    """
    Generate bcrypt password hash.
    
    Args:
        password: Plain text password
        
    Returns:
        Bcrypt hashed password string
    """
    return pwd_context.hash(password)


def create_access_token(
    subject: Union[str, Any], 
    expires_delta: Optional[timedelta] = None
) -> str:
    """
    Create JWT access token.
    
    Args:
        subject: The unique identifier for the user (usually user_id)
        expires_delta: Optional custom expiration time
        
    Returns:
        Encoded JWT string
    """
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(
            minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES
        )
    
    # JWT Payload claims
    to_encode = {
        "sub": str(subject),       # Subject (User ID)
        "exp": expire,             # Expiration time
        "iat": datetime.utcnow(),  # Issued at
        "type": "access"           # Token type
    }
    
    encoded_jwt = jwt.encode(
        to_encode, 
        settings.SECRET_KEY, 
        algorithm=settings.ALGORITHM
    )
    
    return encoded_jwt
