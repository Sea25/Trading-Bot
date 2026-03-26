import argparse
import sys
import os
from dotenv import load_dotenv

from bot.logging_config import setup_logging
from bot.client import BinanceClient
from bot.orders import place_order, build_order_params, format_order_summary, format_order_response

load_dotenv()

def main():
    logger = setup_logging()

    parser = argparse.ArgumentParser(
        description="Binance Futures Testnet Trading Bot",
        formatter_class=argparse.RawTextHelpFormatter
    )
    parser.add_argument("--symbol",      required=True, help="Trading pair, e.g. BTCUSDT")
    parser.add_argument("--side",        required=True, choices=["BUY", "SELL"], help="BUY or SELL")
    parser.add_argument("--type",        required=True, dest="order_type",
                        choices=["MARKET", "LIMIT", "TAKE_PROFIT_MARKET"], help="Order type")
    parser.add_argument("--quantity",    required=True, type=float, help="Order quantity")
    parser.add_argument("--price",       type=float, default=None, help="Limit price (required for LIMIT)")
    parser.add_argument("--stop-price",  type=float, default=None, dest="stop_price",
                        help="Stop price (required for TAKE_PROFIT_MARKET)")

    args = parser.parse_args()

    api_key    = os.getenv("BINANCE_API_KEY")
    api_secret = os.getenv("BINANCE_API_SECRET")

    if not api_key or not api_secret:
        logger.error("API credentials missing. Set BINANCE_API_KEY and BINANCE_API_SECRET in .env")
        sys.exit(1)

    client = BinanceClient(api_key, api_secret)

    try:
        params_preview = build_order_params(
            args.symbol, args.side, args.order_type,
            args.quantity, args.price, args.stop_price
        )
        print("\n" + format_order_summary(params_preview))

        response = place_order(
            client, args.symbol, args.side, args.order_type,
            args.quantity, args.price, args.stop_price
        )

        print("\n" + format_order_response(response))
        print("\n✅ Order placed successfully!\n")

    except ValueError as e:
        print(f"\n❌ Validation Error:\n{e}\n")
        logger.error(f"Validation failed: {e}")
        sys.exit(1)
    except RuntimeError as e:
        print(f"\n❌ API/Network Error: {e}\n")
        logger.error(f"Runtime error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()