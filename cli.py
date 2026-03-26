#!/usr/bin/env python3
"""
Trading Bot CLI — Binance Futures Testnet
Usage examples in README.md
"""

import argparse
import os
import sys

from bot import setup_logging, BinanceClient, BinanceAPIError, place_order, ValidationError


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="trading_bot",
        description="Place orders on Binance Futures Testnet (USDT-M)",
        formatter_class=argparse.RawTextHelpFormatter,
    )

    # ── API credentials ────────────────────────────────────────────────
    creds = parser.add_argument_group("API credentials (or set env vars)")
    creds.add_argument(
        "--api-key",
        default=os.getenv("BINANCE_API_KEY"),
        help="Binance Testnet API key (default: $BINANCE_API_KEY)",
    )
    creds.add_argument(
        "--api-secret",
        default=os.getenv("BINANCE_API_SECRET"),
        help="Binance Testnet API secret (default: $BINANCE_API_SECRET)",
    )

    # ── Sub-commands ───────────────────────────────────────────────────
    subparsers = parser.add_subparsers(dest="command", required=True)

    # place-order
    place = subparsers.add_parser(
        "place-order",
        help="Place a new futures order",
        formatter_class=argparse.RawTextHelpFormatter,
    )
    place.add_argument("--symbol", required=True, help="Trading pair, e.g. BTCUSDT")
    place.add_argument(
        "--side",
        required=True,
        choices=["BUY", "SELL"],
        type=str.upper,
        help="Order side: BUY or SELL",
    )
    place.add_argument(
        "--type",
        dest="order_type",
        required=True,
        choices=["MARKET", "LIMIT", "STOP_MARKET"],
        type=str.upper,
        help="Order type: MARKET | LIMIT | STOP_MARKET",
    )
    place.add_argument("--quantity", required=True, help="Order quantity")
    place.add_argument(
        "--price",
        default=None,
        help="Limit price (required for LIMIT orders)",
    )
    place.add_argument(
        "--stop-price",
        default=None,
        dest="stop_price",
        help="Stop price (required for STOP_MARKET orders)",
    )

    # account
    subparsers.add_parser("account", help="Show account balances and positions")

    # open-orders
    open_ord = subparsers.add_parser("open-orders", help="List open orders")
    open_ord.add_argument("--symbol", default=None, help="Filter by symbol (optional)")

    return parser


def main():
    parser = build_parser()
    args = parser.parse_args()

    # ── Logging ────────────────────────────────────────────────────────
    logger = setup_logging()

    # ── Credentials check ──────────────────────────────────────────────
    if not args.api_key or not args.api_secret:
        parser.error(
            "API credentials are required.\n"
            "Set --api-key / --api-secret flags OR export environment variables:\n"
            "  export BINANCE_API_KEY=your_key\n"
            "  export BINANCE_API_SECRET=your_secret"
        )

    client = BinanceClient(api_key=args.api_key, api_secret=args.api_secret)

    # ── Command dispatch ───────────────────────────────────────────────
    try:
        if args.command == "place-order":
            place_order(
                client=client,
                symbol=args.symbol,
                side=args.side,
                order_type=args.order_type,
                quantity=args.quantity,
                price=args.price,
                stop_price=args.stop_price,
            )

        elif args.command == "account":
            logger.info("Fetching account information")
            data = client.get_account()
            print("\n  ACCOUNT BALANCES (non-zero USDT)")
            print("=" * 60)
            assets = [a for a in data.get("assets", []) if float(a.get("walletBalance", 0)) > 0]
            if assets:
                for asset in assets:
                    print(
                        f"  {asset['asset']:10s}  wallet={asset['walletBalance']}  "
                        f"available={asset['availableBalance']}"
                    )
            else:
                print("  No funded assets found.")
            print("=" * 60)

        elif args.command == "open-orders":
            logger.info("Fetching open orders | symbol=%s", args.symbol)
            orders = client.get_open_orders(symbol=args.symbol)
            print(f"\n  OPEN ORDERS ({len(orders)} found)")
            print("=" * 60)
            if orders:
                for o in orders:
                    print(
                        f"  [{o['orderId']}] {o['symbol']} {o['side']} {o['type']} "
                        f"qty={o['origQty']} price={o['price']} status={o['status']}"
                    )
            else:
                print("  No open orders.")
            print("=" * 60)

    except ValidationError as exc:
        print(f"\n  ✗ Validation error: {exc}\n", file=sys.stderr)
        sys.exit(1)
    except BinanceAPIError as exc:
        print(f"\n  ✗ API error [{exc.code}]: {exc.message}\n", file=sys.stderr)
        sys.exit(1)
    except requests.exceptions.ConnectionError:
        msg = "Network error: could not reach Binance Testnet. Check your connection."
        logger.error(msg)
        print(f"\n  ✗ {msg}\n", file=sys.stderr)
        sys.exit(1)
    except requests.exceptions.Timeout:
        msg = "Request timed out. Binance Testnet may be slow — try again."
        logger.error(msg)
        print(f"\n  ✗ {msg}\n", file=sys.stderr)
        sys.exit(1)
    except Exception as exc:
        logger.exception("Unexpected error: %s", exc)
        print(f"\n  ✗ Unexpected error: {exc}\n", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    import requests  # noqa: F401 — needed for exception handling in main()
    main()