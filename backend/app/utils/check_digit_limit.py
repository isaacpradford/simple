from decimal import Decimal

def check_digit_limit(number, max_digits=500):
    if not isinstance(number, Decimal):
        number = Decimal(number)
    return number.adjusted() + 1 >= max_digits