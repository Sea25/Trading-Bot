import logging

logger = logging.getLogger("trading_bot.validators")

VALID_SIDES = {"BUY", "SELL"}
VALID_ORDER_TYPES = {"MARKET", "LIMIT", "TAKE_PROFIT_MARKET"}

def validate_order_input(symbol: str, side: str, order_type: str, quantity: float, price: float = None, stop_price: float = None):
    errors = []

    if not symbol or not symbol.strip():
        errors.append("Symbol cannot be empty.")
    elif not symbol.upper().endswith("USDT"):
        logger.warning(f"Symbol '{symbol}' does not end with USDT — proceeding anyway.")

    if side.upper() not in VALID_SIDES:
        errors.append(f"Invalid side '{side}'. Must be one of: {VALID_SIDES}")

    if order_type.upper() not in VALID_ORDER_TYPES:
        errors.append(f"Invalid order type '{order_type}'. Must be one of: {VALID_ORDER_TYPES}")

    if quantity <= 0:
        errors.append(f"Quantity must be greater than 0. Got: {quantity}")

    if order_type.upper() == "LIMIT":
        if price is None or price <= 0:
            errors.append("Price is required and must be > 0 for LIMIT orders.")

    if order_type.upper() == "TAKE_PROFIT_MARKET":
        if stop_price is None or stop_price <= 0:
            errors.append("Stop price is required and must be > 0 for TAKE_PROFIT_MARKET orders.")

    if errors:
        for err in errors:
            logger.error(f"Validation error: {err}")
        raise ValueError("\n".join(errors))

    logger.info(f"Validation passed: {order_type} {side} {quantity} {symbol.upper()}")