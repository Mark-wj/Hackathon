import re

def validate_email(email):
    """Validate email format"""
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return re.match(pattern, email) is not None

def validate_password(password):
    """Validate password strength"""
    # At least 8 characters
    return len(password) >= 8

def validate_phone(phone):
    """Validate phone number"""
    # Remove all non-digits
    digits = re.sub(r'\D', '', phone)
    # Check if it's a valid length (10-15 digits)
    return 10 <= len(digits) <= 15

def allowed_file(filename, allowed_extensions):
    """Check if file extension is allowed"""
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in allowed_extensions
