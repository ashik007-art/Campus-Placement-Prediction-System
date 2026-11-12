"""Data validation functions for input fields across the application."""
import re

EMAIL_REGEX = re.compile(r"^[\w\.-]+@([\w-]+\.)+[\w-]{2,63}$")

def validate_email_format(email: str) -> bool:
    """Validate email format using standard regex."""
    if not email or not isinstance(email, str):
        return False
    return bool(EMAIL_REGEX.match(email.strip()))

def validate_percentage(value) -> tuple[bool, str]:
    """Validate percentage value is between 0 and 100."""
    try:
        val = float(value)
        if 0.0 <= val <= 100.0:
            return True, ""
        return False, "Percentage must be between 0.0 and 100.0."
    except (ValueError, TypeError):
        return False, "Invalid numeric value for percentage."

def validate_cgpa(value) -> tuple[bool, str]:
    """Validate CGPA is between 0 and 10."""
    try:
        val = float(value)
        if 0.0 <= val <= 10.0:
            return True, ""
        return False, "CGPA must be between 0.0 and 10.0."
    except (ValueError, TypeError):
        return False, "Invalid numeric value for CGPA."

def validate_non_negative_int(value, field_name="Value") -> tuple[bool, str]:
    """Validate non-negative integer."""
    try:
        val = int(value)
        if val >= 0:
            return True, ""
        return False, f"{field_name} must be a non-negative integer (>= 0)."
    except (ValueError, TypeError):
        return False, f"Invalid integer value for {field_name}."

def validate_password_strength(password: str) -> tuple[bool, str]:
    """Check password length and basic complexity."""
    if not password or len(password) < 6:
        return False, "Password must be at least 6 characters long."
    return True, ""
