import re

def validate_email(email: str) -> bool:
    """Validates an email address format."""
    if not isinstance(email, str):
        raise TypeError("Email must be a string")
    
    # Simple regex for email validation
    pattern = r'^[\w\.-]+@[\w\.-]+\.\w+$'
    return bool(re.match(pattern, email))

def check_password_strength(password: str) -> str:
    """
    Checks password strength. 
    Returns 'Weak', 'Medium', or 'Strong'.
    """
    if not isinstance(password, str):
        raise ValueError("Password must be a string")
        
    length = len(password)
    has_upper = any(c.isupper() for c in password)
    has_digit = any(c.isdigit() for c in password)
    has_special = any(not c.isalnum() for c in password)
    
    score = 0
    if length >= 8: score += 1
    if has_upper: score += 1
    if has_digit: score += 1
    if has_special: score += 1
    
    if score < 2:
        return 'Weak'
    elif score == 2 or score == 3:
        return 'Medium'
    else:
        return 'Strong'
