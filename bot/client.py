import hashlib
import hmac
import time
import urllib.parse
import logging

import requests

logger = logging.getLogger("trading_bot.client")

BASE_URL = "https://testnet.binancefuture.com"
TIMEOUT = 10  # seconds


class BinanceAPIError(Exception):
    """Raised when the Binance API returns an error response."""

    def __init__(self, code: int, message: str):
        self.code = code
        self.message = message
        super().__init__(f"Binance API error {code}: {message}")


class BinanceClient:
    """
    Lightweight wrapper around the Binance Futures Testnet REST API.
    Handles HMAC-SHA256 signing and request execution.
    """

    def __init__(self, api_key: str, api_secret: str):
        self.api_key = api_key
        self.api_secret = api_secret
        self.session = requests.Session()
        self.session.headers.update(
            {
                "X-MBX-APIKEY": self.api_key,
                "Content-Type": "application/x-www-form-urlencoded",
            }
        )

    # ------------------------------------------------------------------
    # Internal helpers
    # ------------------------------------------------------------------

    def _sign(self, params: dict) -> dict:
        """Append a HMAC-SHA256 signature to a param dict."""
        query_string = urllib.parse.urlencode(params)
        signature = hmac.new(
            self.api_secret.encode("utf-8"),
            query_string.encode("utf-8"),
            hashlib.sha256,
        ).hexdigest()
        params["signature"] = signature
        return params

    def _timestamp(self) -> int:
        return int(time.time() * 1000)

    def _handle_response(self, response: requests.Response) -> dict:
        """Parse response, raise BinanceAPIError on non-2xx or API-level errors."""
        logger.debug("Response [%s] %s", response.status_code, response.text)

        try:
            data = response.json()
        except ValueError:
            response.raise_for_status()
            return {}

        if isinstance(data, dict) and "code" in data and data["code"] != 200:
            raise BinanceAPIError(data["code"], data.get("msg", "Unknown error"))

        response.raise_for_status()
        return data

    # ------------------------------------------------------------------
    # Public API methods
    # ------------------------------------------------------------------

    def get_server_time(self) -> dict:
        """Ping the server and return its timestamp (useful for clock sync)."""
        url = f"{BASE_URL}/fapi/v1/time"
        logger.debug("GET %s", url)
        response = self.session.get(url, timeout=TIMEOUT)
        return self._handle_response(response)

    def get_exchange_info(self) -> dict:
        """Return exchange trading rules and symbol information."""
        url = f"{BASE_URL}/fapi/v1/exchangeInfo"
        logger.debug("GET %s", url)
        response = self.session.get(url, timeout=TIMEOUT)
        return self._handle_response(response)

    def get_account(self) -> dict:
        """Return current account information (balances, positions)."""
        url = f"{BASE_URL}/fapi/v2/account"
        params = self._sign({"timestamp": self._timestamp()})
        logger.debug("GET %s params=%s", url, {k: v for k, v in params.items() if k != "signature"})
        response = self.session.get(url, params=params, timeout=TIMEOUT)
        return self._handle_response(response)

    def place_order(
        self,
        symbol: str,
        side: str,
        order_type: str,
        quantity: float,
        price: float = None,
        stop_price: float = None,
        time_in_force: str = "GTC",
    ) -> dict:
        """
        Place a futures order.

        Args:
            symbol:        e.g. 'BTCUSDT'
            side:          'BUY' or 'SELL'
            order_type:    'MARKET', 'LIMIT', or 'STOP_MARKET'
            quantity:      order size
            price:         required for LIMIT
            stop_price:    required for STOP_MARKET
            time_in_force: 'GTC' (default), 'IOC', 'FOK' — only for LIMIT
        """
        url = f"{BASE_URL}/fapi/v1/order"

        params: dict = {
            "symbol": symbol,
            "side": side,
            "type": order_type,
            "quantity": quantity,
            "timestamp": self._timestamp(),
        }

        if order_type == "LIMIT":
            if price is None:
                raise ValueError("price is required for LIMIT orders")
            params["price"] = price
            params["timeInForce"] = time_in_force

        if order_type == "STOP_MARKET":
            if stop_price is None:
                raise ValueError("stop_price is required for STOP_MARKET orders")
            params["stopPrice"] = stop_price

        self._sign(params)

        # Log request without the signature
        safe_params = {k: v for k, v in params.items() if k != "signature"}
        logger.info("Placing order | params=%s", safe_params)

        response = self.session.post(url, data=params, timeout=TIMEOUT)
        return self._handle_response(response)

    def cancel_order(self, symbol: str, order_id: int) -> dict:
        """Cancel an open order by orderId."""
        url = f"{BASE_URL}/fapi/v1/order"
        params = self._sign(
            {"symbol": symbol, "orderId": order_id, "timestamp": self._timestamp()}
        )
        logger.info("Cancelling order | symbol=%s orderId=%s", symbol, order_id)
        response = self.session.delete(url, params=params, timeout=TIMEOUT)
        return self._handle_response(response)

    def get_open_orders(self, symbol: str = None) -> list:
        """Return all open orders, optionally filtered by symbol."""
        url = f"{BASE_URL}/fapi/v1/openOrders"
        params: dict = {"timestamp": self._timestamp()}
        if symbol:
            params["symbol"] = symbol
        self._sign(params)
        logger.debug("GET open orders | symbol=%s", symbol)
        response = self.session.get(url, params=params, timeout=TIMEOUT)
        return self._handle_response(response)