# sample_repo/string_utils.py

def reverse_string(s: str) -> str:
    """Reverses a given string. Raises TypeError if input is not a string."""
    if not isinstance(s, str):
        raise TypeError("Input must be a string.")
    return s[::-1]

def is_palindrome(s: str) -> bool:
    """Checks if a string is a palindrome ignoring case and spaces."""
    if not isinstance(s, str):
        raise TypeError("Input must be a string.")
    cleaned = "".join(c.lower() for c in s if c.isalnum())
    return cleaned == cleaned[::-1]
