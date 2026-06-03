from fastapi import HTTPException, Request, status
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
from sqlalchemy.exc import IntegrityError


class Placement360Exception(Exception):
    """Base exception for Placement360 application."""
    
    def __init__(self, message: str, status_code: int = 500):
        self.message = message
        self.status_code = status_code
        super().__init__(self.message)


class DatabaseException(Placement360Exception):
    """Database operation failed."""
    pass


class AuthenticationException(Placement360Exception):
    """Authentication failed."""
    
    def __init__(self, message: str = "Authentication failed", **kwargs):
        super().__init__(message, status_code=401)


class AuthorizationException(Placement360Exception):
    """User not authorized for action."""
    
    def __init__(self, message: str = "Not authorized", **kwargs):
        super().__init__(message, status_code=403)


class NotFoundException(Placement360Exception):
    """Resource not found."""
    
    def __init__(self, message: str = "Resource not found", resource: str = None, identifier: str = None, code: str = None, **kwargs):
        if resource and identifier:
            message = f"{resource} with identifier '{identifier}' not found"
        super().__init__(message, status_code=404)


class ValidationException(Placement360Exception):
    """Request validation failed."""
    
    def __init__(self, message: str, code: str = None, field_errors: list = None, **kwargs):
        super().__init__(message, status_code=422)
        self.code = code
        self.field_errors = field_errors


class ExternalAPIException(Placement360Exception):
    """External API call failed."""
    
    def __init__(self, service: str, message: str):
        super().__init__(f"{service} API error: {message}", status_code=503)


async def placement360_exception_handler(
    request: Request,
    exc: Placement360Exception
) -> JSONResponse:
    """Handle custom Placement360 exceptions."""
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "detail": exc.message,
            "error_type": exc.__class__.__name__
        }
    )


async def database_exception_handler(
    request: Request,
    exc: IntegrityError
) -> JSONResponse:
    """Handle SQLAlchemy integrity errors."""
    return JSONResponse(
        status_code=status.HTTP_409_CONFLICT,
        content={
            "detail": "Database constraint violation",
            "error": str(exc.orig)
        }
    )


from fastapi.encoders import jsonable_encoder
import logging

logger = logging.getLogger(__name__)

import json

async def validation_exception_handler(
    request: Request, 
    exc: RequestValidationError
) -> JSONResponse:
    # Convert errors to JSON-safe format
    errors = []
    for error in exc.errors():
        safe_error = {
            "loc": error.get("loc", []),
            "msg": str(error.get("msg", "Validation error")),
            "type": error.get("type", "value_error"),
        }
        # Handle ctx safely
        if "ctx" in error:
            try:
                safe_error["ctx"] = json.loads(
                    json.dumps(error["ctx"], default=str)
                )
            except Exception:
                safe_error["ctx"] = str(error["ctx"])
        
        errors.append(safe_error)
    
    return JSONResponse(
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        content={"detail": errors}
    )
