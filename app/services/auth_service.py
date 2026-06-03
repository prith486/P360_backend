from typing import Optional
from sqlalchemy.orm import Session
from app.core.security import verify_password, get_password_hash, create_access_token
from app.models.user import User


class AuthService:
    """Authentication business logic."""
    
    @staticmethod
    def authenticate_user(
        db: Session,
        email: str,
        password: str
    ) -> Optional[User]:
        """
        Authenticate user with email and password.
        
        Returns:
            User object if authentication successful, None otherwise
        """
        # TODO: Implement authentication logic
        # 1. Query user by email
        # 2. Verify password using verify_password()
        # 3. Return user if valid, None otherwise
        pass
    
    @staticmethod
    def register_user(
        db: Session,
        email: str,
        password: str,
        role: str,
        **kwargs
    ) -> User:
        """
        Register new user.
        
        Returns:
            Created user object
        """
        # TODO: Implement registration logic
        # 1. Check if email already exists
        # 2. Hash password using get_password_hash()
        # 3. Create user record
        # 4. Create role-specific profile (student/faculty/admin)
        pass
    
    @staticmethod
    def create_user_token(user: User) -> dict:
        """
        Create access and refresh tokens for user.
        
        Returns:
            Dictionary with access_token and refresh_token
        """
        # TODO: Implement token creation
        # 1. Create access token with user ID
        # 2. Create refresh token
        # 3. Return both tokens
        pass


auth_service = AuthService()
