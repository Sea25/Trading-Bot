import logging
from typing import Optional

from .client import BinanceClient, BinanceAPIError
from .validators import validate_order_inputs, ValidationError

logger = logging.getLogger("trading_bot.orders")


def _print_separator():
    print("=" * 60)


def _print_request_summary(params: dict):
    _print_separator()
    print("  ORDER REQUEST SUMMARY")
    _print_separator()
    print(f"  Symbol     : {params['symbol']}")
    print(f"  Side       : {params['side']}")
    print(f"  Type       : {params['order_type']}")
    print(f"  Quantity   : {params['quantity']}")
    if "price" in params:
        print(f"  Price      : {params['price']}")
    if "stop_price" in params:
        print(f"  Stop Price : {params['stop_price']}")
    _print_separator()


def _print_order_response(response: dict):
    print("  ORDER RESPONSE")
    _print_separator()
    print(f"  Order ID      : {response.get('orderId', 'N/A')}")
    print(f"  Client OID    : {response.get('clientOrderId', 'N/A')}")
    print(f"  Symbol        : {response.get('symbol', 'N/A')}")
    print(f"  Side          : {response.get('side', 'N/A')}")
    print(f"  Type          : {response.get('type', 'N/A')}")
    print(f"  Status        : {response.get('status', 'N/A')}")
    print(f"  Orig Qty      : {response.get('origQty', 'N/A')}")
    print(f"  Executed Qty  : {response.get('executedQty', 'N/A')}")

    avg_price = response.get("avgPrice") or response.get("price", "N/A")
    print(f"  Avg Price     : {avg_price}")

    if response.get("stopPrice") and response["stopPrice"] != "0":
        print(f"  Stop Price    : {response['stopPrice']}")

    print(f"  Time In Force : {response.get('timeInForce', 'N/A')}")
    _print_separator()


def place_order(
    client: BinanceClient,
    symbol: str,
    side: str,
    order_type: str,
    quantity: str,
    price: Optional[str] = None,
    stop_price: Optional[str] = None,
) -> dict:
    """
    Validate inputs, place the order, print output, and return the response dict.
    Raises ValidationError or BinanceAPIError on failure.
    """
    # Validate
    try:
        params = validate_order_inputs(
            symbol=symbol,
            side=side,
            order_type=order_type,
            quantity=quantity,
            price=price,
            stop_price=stop_price,
        )
    except ValidationError as exc:
        logger.error("Validation failed: %s", exc)
        raise

    _print_request_summary(params)

    # Place order
    try:
        response = client.place_order(
            symbol=params["symbol"],
            side=params["side"],
            order_type=params["order_type"],
            quantity=params["quantity"],
            price=params.get("price"),
            stop_price=params.get("stop_price"),
        )
    except BinanceAPIError as exc:
        logger.error("API error while placing order: %s", exc)
        print(f"\n  ✗ Order FAILED — {exc}\n")
        raise
    except Exception as exc:
        logger.error("Unexpected error while placing order: %s", exc)
        print(f"\n  ✗ Order FAILED — {exc}\n")
        raise

    logger.info(
        "Order placed successfully | orderId=%s status=%s executedQty=%s",
        response.get("orderId"),
        response.get("status"),
        response.get("executedQty"),
    )

    _print_order_response(response)
    print(f"  ✓ Order placed successfully!\n")

    return response