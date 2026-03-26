import requests
import time
import hashlib
import hmac
import urllib.parse
from .logging_config import setup_logging

logger = setup_logging()

class BinanceFuturesClient:
    def __init__(self, api_key, secret_key):
        self.api_key = api_key
        self.secret_key = secret_key
        self.base_url = "https://testnet.binancefuture.com"
        self.session = requests.Session()
        self.session.headers.update({
            'X-MBX-APIKEY': api_key,
            'Content-Type': 'application/json'
        })
        
    def _generate_signature(self, params):
        """Generate HMAC SHA256 signature for API request"""
        query_string = urllib.parse.urlencode(params)
        signature = hmac.new(
            self.secret_key.encode('utf-8'),
            query_string.encode('utf-8'),
            hashlib.sha256
        ).hexdigest()
        return signature
    
    def _make_request(self, method, endpoint, signed=False, params=None):
        """Make API request to Binance"""
        url = f"{self.base_url}{endpoint}"
        
        if signed:
            if params is None:
                params = {}
            params['timestamp'] = int(time.time() * 1000)
            params['signature'] = self._generate_signature(params)
        
        try:
            if method == "GET":
                response = self.session.get(url, params=params)
            elif method == "POST":
                response = self.session.post(url, params=params, json=params if signed else None)
            else:
                raise ValueError(f"Unsupported method: {method}")
            
            response.raise_for_status()
            logger.debug(f"Request successful: {endpoint}")
            return response.json()
            
        except requests.exceptions.RequestException as e:
            logger.error(f"API request failed: {e}")
            if hasattr(e, 'response') and e.response:
                logger.error(f"Response: {e.response.text}")
            raise
    
    def get_account_info(self):
        """Get account information"""
        return self._make_request("GET", "/fapi/v2/account", signed=True)
    
    def place_order(self, symbol, side, order_type, quantity, price=None):
        """
        Place an order on Binance Futures
        side: BUY or SELL
        order_type: MARKET or LIMIT
        """
        params = {
            'symbol': symbol,
            'side': side,
            'type': order_type,
            'quantity': quantity
        }
        
        # Add price for limit orders
        if order_type == 'LIMIT':
            params['price'] = price
            params['timeInForce'] = 'GTC'  # Good Till Cancelled
        
        logger.info(f"Placing order: {side} {order_type} {quantity} {symbol}" + 
                   (f" @ {price}" if price else ""))
        
        try:
            response = self._make_request("POST", "/fapi/v1/order", signed=True, params=params)
            logger.info(f"Order placed successfully! Order ID: {response['orderId']}")
            return response
        except Exception as e:
            logger.error(f"Failed to place order: {e}")
            raise