import logging
from .client import BinanceClient
from .validators import validate_order_input

logger = logging.getLogger("trading_bot.orders")

def build_order_params(symbol, side, order_type, quantity, price=None, stop_price=None):
    params = {
        "symbol": symbol.upper(),
        "side": side.upper(),
        "type": order_type.upper(),
        "quantity": quantity,
    }
    if order_type.upper() == "LIMIT":
        params["price"] = price
        params["timeInForce"] = "GTC"
    if order_type.upper() == "STOP_MARKET":
        params["stopPrice"] = stop_price
        params["closePosition"] = "true"
    return params

def place_order(client: BinanceClient, symbol: str, side: str, order_type: str,
                quantity: float, price: float | None = None, stop_price: float | None = None) -> dict:
    validate_order_input(symbol, side, order_type, quantity, price, stop_price)

    params = build_order_params(symbol, side, order_type, quantity, price, stop_price)

    logger.info(f"Placing order: {params}")
    response = client.place_order(params)
    logger.info(f"Order placed successfully. OrderId: {response.get('orderId')} | Status: {response.get('status')}")
    return response

def format_order_summary(params: dict) -> str:
    lines = [
        "─── Order Request Summary ───",
        f"  Symbol     : {params.get('symbol')}",
        f"  Side       : {params.get('side')}",
        f"  Type       : {params.get('type')}",
        f"  Quantity   : {params.get('quantity')}",
    ]
    if params.get("price"):
        lines.append(f"  Price      : {params.get('price')}")
    if params.get("stopPrice"):
        lines.append(f"  Stop Price : {params.get('stopPrice')}")
    return "\n".join(lines)

def format_order_response(response: dict) -> str:
    return "\n".join([
        "─── Order Response ───",
        f"  Order ID    : {response.get('orderId')}",
        f"  Status      : {response.get('status')}",
        f"  Executed Qty: {response.get('executedQty')}",
        f"  Avg Price   : {response.get('avgPrice', 'N/A')}",
        f"  Client OID  : {response.get('clientOrderId', 'N/A')}",
    ])