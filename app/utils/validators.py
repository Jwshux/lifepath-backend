import re

EMAIL_PATTERN = re.compile(r'^[^\s@]+@[^\s@]+\.[^\s@]+$')


def is_valid_email(email):
    return bool(email) and bool(EMAIL_PATTERN.match(email))


def is_valid_password(password):
    # Minimum 8 characters, at least one letter and one number.
    if not password or len(password) < 8:
        return False
    has_letter = any(char.isalpha() for char in password)
    has_number = any(char.isdigit() for char in password)
    return has_letter and has_number