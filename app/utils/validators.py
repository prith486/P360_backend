import re
from typing import Optional


def validate_email(email: str) -> bool:
    """Validate email format."""
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return bool(re.match(pattern, email))


def validate_cgpa(cgpa: float) -> bool:
    """Validate CGPA is between 0 and 10."""
    if cgpa is None: return False
    return 0.0 <= cgpa <= 10.0


def validate_code_language(language: str) -> bool:
    """Validate programming language is supported."""
    supported = ["python", "java", "cpp", "javascript", "c"]
    return language.lower() in supported


def sanitize_filename(filename: str) -> str:
    """Remove dangerous characters from filename."""
    return re.sub(r'[^a-zA-Z0-9_.-]', '', filename)
