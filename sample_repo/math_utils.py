# sample_repo/math_utils.py

def divide(a: float, b: float) -> float:
    """Divides a by b. Raises ValueError if b is 0."""
    if b == 0:
        raise ValueError("Cannot divide by zero.")
    return a / b

def is_prime(n: int) -> bool:
    """Checks if a number is prime."""
    if n <= 1:
        return False
    for i in range(2, int(n**0.5) + 1):
        if n % i == 0:
            return False
    return True
