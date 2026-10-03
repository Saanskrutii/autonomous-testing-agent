def calculate_discount(price: float, discount_percent: float) -> float:
    """
    Calculates final price after applying a discount percentage.
    Raises ValueError for invalid inputs.
    """
    if price < 0:
        raise ValueError("Price cannot be negative")
    if not (0 <= discount_percent <= 100):
        raise ValueError("Discount must be between 0 and 100")
        
    discount_amount = price * (discount_percent / 100)
    return round(price - discount_amount, 2)

def calculate_emi(principal: float, annual_rate: float, months: int) -> float:
    """
    Calculates monthly EMI for a loan.
    """
    if principal <= 0 or months <= 0:
        raise ValueError("Principal and months must be positive")
    
    if annual_rate == 0:
        return round(principal / months, 2)
        
    monthly_rate = annual_rate / 12 / 100
    emi = principal * monthly_rate * ((1 + monthly_rate) ** months) / (((1 + monthly_rate) ** months) - 1)
    return round(emi, 2)
