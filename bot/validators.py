VALID_SIDES = {"BUY", "SELL"}
VALID_ORDER_TYPES = {"MARKET", "LIMIT", "STOP_MARKET"}


class ValidationError(Exception):
    """Raised when user input fails validation."""
    pass


def validate_symbol(symbol: str) -> str:
    symbol = symbol.strip().upper()
    if not symbol.isalnum():
        raise ValidationError(f"Invalid symbol '{symbol}'. Must be alphanumeric, e.g. BTCUSDT.")
    return symbol


def validate_side(side: str) -> str:
    side = side.strip().upper()
    if side not in VALID_SIDES:
        raise ValidationError(f"Invalid side '{side}'. Must be one of: {', '.join(VALID_SIDES)}.")
    return side


def validate_order_type(order_type: str) -> str:
    order_type = order_type.strip().upper()
    if order_type not in VALID_ORDER_TYPES:
        raise ValidationError(
            f"Invalid order type '{order_type}'. Must be one of: {', '.join(VALID_ORDER_TYPES)}."
        )
    return order_type


def validate_quantity(quantity: str) -> float:
    try:
        qty = float(quantity)
    except (ValueError, TypeError):
        raise ValidationError(f"Invalid quantity '{quantity}'. Must be a positive number.")
    if qty <= 0:
        raise ValidationError(f"Quantity must be greater than 0, got {qty}.")
    return qty


def validate_price(price: str) -> float:
    try:
        p = float(price)
    except (ValueError, TypeError):
        raise ValidationError(f"Invalid price '{price}'. Must be a positive number.")
    if p <= 0:
        raise ValidationError(f"Price must be greater than 0, got {p}.")
    return p


def validate_stop_price(stop_price: str) -> float:
    try:
        sp = float(stop_price)
    except (ValueError, TypeError):
        raise ValidationError(f"Invalid stop price '{stop_price}'. Must be a positive number.")
    if sp <= 0:
        raise ValidationError(f"Stop price must be greater than 0, got {sp}.")
    return sp


def validate_order_inputs(
    symbol: str,
    side: str,
    order_type: str,
    quantity: str,
    price: str = None,
    stop_price: str = None,
) -> dict:
    """
    Validate all order inputs together and return a clean dict.
    Raises ValidationError on the first problem found.
    """
    cleaned = {
        "symbol": validate_symbol(symbol),
        "side": validate_side(side),
        "order_type": validate_order_type(order_type),
        "quantity": validate_quantity(quantity),
    }

    if cleaned["order_type"] == "LIMIT":
        if not price:
            raise ValidationError("Price is required for LIMIT orders.")
        cleaned["price"] = validate_price(price)

    if cleaned["order_type"] == "STOP_MARKET":
        if not stop_price:
            raise ValidationError("Stop price (--stop-price) is required for STOP_MARKET orders.")
        cleaned["stop_price"] = validate_stop_price(stop_price)

    return cleaned