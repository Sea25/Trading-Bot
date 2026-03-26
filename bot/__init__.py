#!/usr/bin/env python3
import argparse
import sys
import os
from dotenv import load_dotenv
from bot.client import BinanceFuturesClient
from bot.logging_config import setup_logging

# Load environment variables
load_dotenv()

# Setup logging
logger = setup_logging()

def validate_input(args):
    """Validate user input"""
    # Check symbol
    if not args.symbol:
        raise ValueError("Symbol is required")
    
    # Check side
    if args.side not in ['BUY', 'SELL']:
        raise ValueError("Side must be BUY or SELL")
    
    # Check order type
    if args.order_type not in ['MARKET', 'LIMIT']:
        raise ValueError("Order type must be MARKET or LIMIT")
    
    # Check quantity
    try:
        quantity = float(args.quantity)
        if quantity <= 0:
            raise ValueError("Quantity must be positive")
    except ValueError:
        raise ValueError("Quantity must be a valid number")
    
    # Check price for limit orders
    if args.order_type == 'LIMIT':
        if not args.price:
            raise ValueError("Price is required for LIMIT orders")
        try:
            price = float(args.price)
            if price <= 0:
                raise ValueError("Price must be positive")
        except ValueError:
            raise ValueError("Price must be a valid number")
    
    return True

def main():
    parser = argparse.ArgumentParser(description='Trading Bot for Binance Futures Testnet')
    
    parser.add_argument('--symbol', required=True, help='Trading pair (e.g., BTCUSDT)')
    parser.add_argument('--side', required=True, choices=['BUY', 'SELL'], help='BUY or SELL')
    parser.add_argument('--order-type', required=True, choices=['MARKET', 'LIMIT'], help='MARKET or LIMIT')
    parser.add_argument('--quantity', required=True, help='Order quantity')
    parser.add_argument('--price', help='Price for LIMIT orders')
    
    args = parser.parse_args()
    
    # Print order summary
    print("\n" + "="*50)
    print("ORDER SUMMARY")
    print("="*50)
    print(f"Symbol: {args.symbol}")
    print(f"Side: {args.side}")
    print(f"Order Type: {args.order_type}")
    print(f"Quantity: {args.quantity}")
    if args.price:
        print(f"Price: {args.price}")
    print("="*50)
    
    try:
        # Validate input
        validate_input(args)
        
        # Get API credentials
        api_key = os.getenv('API_KEY')
        secret_key = os.getenv('SECRET_KEY')
        
        if not api_key or not secret_key:
            raise ValueError("API credentials not found. Please check .env file")
        
        # Create client
        client = BinanceFuturesClient(api_key, secret_key)
        
        # Place order
        response = client.place_order(
            symbol=args.symbol,
            side=args.side,
            order_type=args.order_type,
            quantity=float(args.quantity),
            price=float(args.price) if args.price else None
        )
        
        # Print success response
        print("\n✅ ORDER SUCCESSFUL!")
        print("-"*50)
        print(f"Order ID: {response['orderId']}")
        print(f"Status: {response['status']}")
        print(f"Executed Quantity: {response.get('executedQty', 0)}")
        print(f"Avg Price: {response.get('avgPrice', 'N/A')}")
        print("-"*50)
        
        logger.info(f"Order completed successfully. Order ID: {response['orderId']}")
        
    except ValueError as e:
        print(f"\n❌ VALIDATION ERROR: {e}")
        logger.error(f"Validation error: {e}")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ ERROR: Failed to place order")
        print(f"Details: {e}")
        logger.error(f"Order failed: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()