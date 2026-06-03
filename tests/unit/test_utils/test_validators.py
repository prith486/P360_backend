import pytest
from app.utils.validators import validate_email, validate_cgpa, validate_code_language


class TestValidators:
    """Unit tests for validation utilities."""
    
    def test_validate_email_valid(self):
        """Test email validation with valid emails."""
        assert validate_email("student@college.edu") == True
        assert validate_email("faculty123@university.ac.in") == True
    
    def test_validate_email_invalid(self):
        """Test email validation with invalid emails."""
        assert validate_email("notanemail") == False
        assert validate_email("missing@domain") == False
        assert validate_email("@nodomain.com") == False
    
    def test_validate_cgpa_valid(self):
        """Test CGPA validation with valid scores."""
        assert validate_cgpa(8.5) == True
        assert validate_cgpa(0.0) == True
        assert validate_cgpa(10.0) == True
    
    def test_validate_cgpa_invalid(self):
        """Test CGPA validation with invalid scores."""
        assert validate_cgpa(-1.0) == False
        assert validate_cgpa(11.0) == False
    
    def test_validate_code_language_valid(self):
        """Test language validation with supported languages."""
        assert validate_code_language("python") == True
        assert validate_code_language("JAVA") == True  # Case insensitive
    
    def test_validate_code_language_invalid(self):
        """Test language validation with unsupported languages."""
        assert validate_code_language("rust") == False
        assert validate_code_language("unknown") == False
