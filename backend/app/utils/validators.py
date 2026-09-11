import re


def validate_indian_phone(phone: str) -> bool:
    """Validate 10-digit Indian phone numbers."""
    pattern = r"^[6-9]\d{9}$"
    return bool(re.match(pattern, phone.strip()))


def validate_pin_code(pincode: str) -> bool:
    """Validate 6-digit Indian PIN code."""
    pattern = r"^[1-9][0-9]{5}$"
    return bool(re.match(pattern, pincode.strip()))
